import os
import argparse
import yaml
import sys
import cPickle as pickle
import codecs

def _parse_cmdline():

    parser = argparse.ArgumentParser()
    parser.add_argument('-ti', '--test-instances',
                        help=u'File of pickled test instances',
                        type=unicode, required=True)
    
    parser.add_argument('-ci', '--class-instances', 
                        help=u'File of pickled class instances',
                        type=unicode, required=True)

    parser.add_argument('-of', '--outputfile', 
                        help=u'Output file to write category type, \
                              disaster name, and instance path.',
                        type=unicode, required=True)

    parser.add_argument('-mf', '--metricsfile', 
                        help=u'Output file to write classifier accuracy.',
                        type=unicode, required=True)

    parser.add_argument('-m', '--mode',
                        help=u'Classification mode (cascade|single)',
                        type=unicode, default='single')



    args = parser.parse_args()
    testfile = args.test_instances
    classfile = args.class_instances
    ofile = args.outputfile
    mfile = args.metricsfile
    mode = args.mode

    if os.path.isdir(testfile):
        sys.stderr.write((u'Test instance pickle file {} '
                          + 'is a directory!\n').format(testfile))
        sys.stderr.flush()
        sys.exit()
    if os.path.isdir(classfile):
        sys.stderr.write((u'Class instance pickle file {} '
                          + 'is a directory!\n').format(classfile))
        sys.stderr.flush()
        sys.exit()

    if os.path.isdir(mfile):
        sys.stderr.write((u'Metrics file {} '
                          + 'is a directory!\n').format(mfile))
        sys.stderr.flush()
        sys.exit()
 
    odir = os.path.split(ofile)[0]
    if odir != '' and not os.path.exists(odir):
        os.makedirs(odir)
    
    if os.path.isdir(ofile):
        sys.stderr.write((u'Output file {} '
                          + 'is a directory!\n').format(ofile))
        sys.stderr.flush()
        sys.exit()

    if mode not in ('cascade', 'single'):
        mode = 'single'

    return testfile, classfile, ofile, mfile, mode

def build_single_classier(classfile):

    points = []
    with open(classfile, 'rb') as cf:
        ninstances = pickle.load(cf)
        for _ in range(ninstances):
            inst = pickle.load(cf)
            points.append(inst)

    def classify(inst):
        
        max_point = None
        max_sim = float('-inf') 
        for p in points:
            sim = p['vector'].dot(inst['vector'])[0, 0]       
            if sim > max_sim:
                max_point = p
                max_sim = sim
        if max_point is not None:
            return max_point, max_sim
        else:
            return None, None
    return classify

def build_cascade_classifier(classfile):
  
    import itertools 
    class_centroids = {}
    class_points = {}
    with open(classfile, 'rb') as cf:
        ninstances = pickle.load(cf)
        for _ in range(ninstances):
            inst = pickle.load(cf)
            c_inst = inst['class'] 
            if c_inst not in class_centroids:
                class_centroids[c_inst] = inst['vector']
                class_points[c_inst] = [inst]
            else:
                vcoo = inst['vector'].tocoo()
                for i, j, val in itertools.izip(vcoo.row, vcoo.col, vcoo.data):
                    class_centroids[c_inst][i,j] += val
                class_points[c_inst].append(inst)
        for c_inst in class_centroids.keys():
            npoints = len(class_points[c_inst])
            class_centroids[c_inst] = class_centroids[c_inst] / float(npoints) 

    def classify(inst):

        max_class = None
        max_class_sim = float('-inf') 
        for c, cv in class_centroids.items():
            sim = cv.dot(inst['vector'])[0, 0]       
            if sim > max_class_sim:
                max_class = c
                max_class_sim = sim
        if max_class is None:
            return None, None
        else:
            max_point = None
            max_sim = None
            max_sim = float('-inf') 
            for p in class_points[max_class]:
                sim = p['vector'].dot(inst['vector'])[0, 0]       
                if sim > max_sim:
                    max_point = p
                    max_sim = sim
            if max_point is not None:
                return max_point, max_sim
            else:
                return None, None
    return classify

def main():

    testfile, classfile, ofile, mfile, mode = _parse_cmdline()

    print u'Building classifier...'
    if mode == 'single':
        classify = build_single_classier(classfile)
    elif mode == 'cascade':
        classify = build_cascade_classifier(classfile)

    predictions = []

    class_correct = 0
    disaster_correct = 0
        
    with open(testfile, 'rb') as tf:
        ninstances = pickle.load(tf)
        for idx in range(ninstances):
            inst = pickle.load(tf)
            inst_fname = os.path.split(inst['file'])[1]
            point, score = classify(inst)
            if point is not None:
                predictions.append((point['class'],
                                    point['disaster'],
                                    score,
                                    inst_fname))
                          
                if point['class'] == inst['class']:
                    class_correct += 1
                if point['disaster'] == inst['disaster']:
                    disaster_correct += 1
            
            else:
                predictions.append(('N/A',
                                    'N/A',
                                    0.0,
                                    inst_fname))
            per = 100.0 * float(idx + 1) / ninstances
            sys.stdout.write(u'\rClassifying: {:2.3f}%'.format(per))
            sys.stdout.flush()

        print u'\rClassifying: 100%     '

    print u'Writing output...'
    with codecs.open(ofile, 'w', 'utf-8') as of:
        for p in sorted(predictions, key=lambda x: x[3]):
            of.write(u'{}\t{}\t{}\t{}\n'.format(p[0], p[1], p[2], p[3]))
            of.flush()

    class_acc = class_correct / float(ninstances)
    disaster_acc = disaster_correct / float(ninstances)
    classfname = os.path.split(classfile)[1]
    
    print u'class_file: {}'.format(classfname)
    print u'Mode: {}'.format(mode)
    print u'Class Acc: {}'.format(class_acc)
    print u'Disaster Acc: {}'.format(disaster_acc)
    
    if not os.path.exists(mfile):
        with codecs.open(mfile, 'w', 'utf-8') as mf:
            mf.write('classfname\tmode\tclass_acc\tdisaster_acc')
            mf.write('\n{}\t{}\t{}\t{}'.format(classfname, mode,
                                               class_acc, disaster_acc))
    else:
        with codecs.open(mfile, 'a', 'utf-8') as mf:
            mf.write('\n{}\t{}\t{}\t{}'.format(classfname, mode,
                                               class_acc, disaster_acc))

    print u'Complete!'

if __name__ == u'__main__':
    main()
