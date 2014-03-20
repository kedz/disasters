ROOTDIR="${HOME}/experiments/disasters/link_classification"
CLASS_OUT="${ROOTDIR}/classifier_output"
INST_VEC="${ROOTDIR}/instance_vectors"
CLASS_VEC="${ROOTDIR}/class_vectors"
RESULTS="${ROOTDIR}/classification_results.txt"
DATA="/home/kedz/data/disaster_wikis"
DF="${ROOTDIR}/doc_freqs"


echo
echo "### 2A) Running Abstract UnSeparated ###"
echo "========================================"

echo
echo "Building document frequencies..."
echo "================================"
python docfreq.py -id ${DATA}/xml/abstract_text -of ${DF}/abs_unsep_txt_all_df.p

echo
echo "Building instance vectors..."
echo "================================"
python create_instance_vectors.py -id ${DATA}/linked_pages_xml/ -df ${DF}/abs_unsep_txt_all_df.p -of ${INST_VEC}/linked_pages_abs_instances.p

echo
echo "Building class vectors..."
echo "================================"
echo "Creating unnormed class vectors..."
python create_class_vectors.py -id ${DATA}/xml/abstract_text/ -df ${DF}/abs_unsep_txt_all_df.p -of ${CLASS_VEC}/abs_unsep_unnorm_class_vectors.p
echo "--"
echo "Creating normed class vectors..."
python create_class_vectors.py -id ${DATA}/xml/abstract_text/ -df ${DF}/abs_unsep_txt_all_df.p -of ${CLASS_VEC}/abs_unsep_norm_class_vectors.p -n

echo
echo "Classification..."
echo "================================"

echo "Single unnormed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_abs_instances.p -ci ${CLASS_VEC}/abs_unsep_unnorm_class_vectors.p -of ${CLASS_OUT}/abs_unsep_unnorm_single_class.txt -m single -mf ${RESULTS}
echo
echo "Single normed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_abs_instances.p -ci ${CLASS_VEC}/abs_unsep_norm_class_vectors.p -of ${CLASS_OUT}/abs_unsep_norm_single_class.txt -m single -mf ${RESULTS}

echo
echo "--"

echo
echo "Cascade unnormed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_abs_instances.p -ci ${CLASS_VEC}/abs_unsep_unnorm_class_vectors.p -of ${CLASS_OUT}/abs_unsep_unnorm_cascade_class.txt -m cascade -mf ${RESULTS}
echo
echo "Cascade normed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_abs_instances.p -ci ${CLASS_VEC}/abs_unsep_norm_class_vectors.p -of ${CLASS_OUT}/abs_unsep_norm_cascade_class.txt -m cascade -mf ${RESULTS}


echo
echo "### 2B) Running Impact UnSeparated ###"
echo "======================================"

echo
echo "Building document frequencies..."
echo "================================"
python docfreq.py -id ${DATA}/xml/impact_text -of ${DF}/imp_unsep_txt_all_df.p

echo
echo "Building instance vectors..."
echo "================================"
python create_instance_vectors.py -id ${DATA}/linked_pages_xml/ -df ${DF}/imp_unsep_txt_all_df.p -of ${INST_VEC}/linked_pages_imp_instances.p

echo
echo "Building class vectors..."
echo "================================"
echo "Creating unnormed class vectors..."
python create_class_vectors.py -id ${DATA}/xml/impact_text/ -df ${DF}/imp_unsep_txt_all_df.p -of ${CLASS_VEC}/imp_unsep_unnorm_class_vectors.p
echo "--"
echo "Creating normed class vectors..."
python create_class_vectors.py -id ${DATA}/xml/impact_text/ -df ${DF}/imp_unsep_txt_all_df.p -of ${CLASS_VEC}/imp_unsep_norm_class_vectors.p -n

echo
echo "Classification..."
echo "================================"

echo "Single unnormed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_imp_instances.p -ci ${CLASS_VEC}/imp_unsep_unnorm_class_vectors.p -of ${CLASS_OUT}/imp_unsep_unnorm_single_class.txt -m single -mf ${RESULTS}
echo
echo "Single normed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_imp_instances.p -ci ${CLASS_VEC}/imp_unsep_norm_class_vectors.p -of ${CLASS_OUT}/imp_unsep_norm_single_class.txt -m single -mf ${RESULTS}

echo
echo "--"

echo
echo "Cascade unnormed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_imp_instances.p -ci ${CLASS_VEC}/imp_unsep_unnorm_class_vectors.p -of ${CLASS_OUT}/imp_unsep_unnorm_cascade_class.txt -m cascade -mf ${RESULTS}
echo
echo "Cascade normed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_imp_instances.p -ci ${CLASS_VEC}/imp_unsep_norm_class_vectors.p -of ${CLASS_OUT}/imp_unsep_norm_cascade_class.txt -m cascade -mf ${RESULTS}



echo
echo "### 2C) Running History UnSeparated  ###"
echo "========================================"

echo
echo "Building document frequencies..."
echo "================================"
python docfreq.py -id ${DATA}/xml/history_text -of ${DF}/his_unsep_txt_all_df.p

echo
echo "Building instance vectors..."
echo "================================"
python create_instance_vectors.py -id ${DATA}/linked_pages_xml/ -df ${DF}/his_unsep_txt_all_df.p -of ${INST_VEC}/linked_pages_his_instances.p

echo
echo "Building class vectors..."
echo "================================"
echo "Creating unnormed class vectors..."
python create_class_vectors.py -id ${DATA}/xml/history_text/ -df ${DF}/his_unsep_txt_all_df.p -of ${CLASS_VEC}/his_unsep_unnorm_class_vectors.p
echo "--"
echo "Creating normed class vectors..."
python create_class_vectors.py -id ${DATA}/xml/history_text/ -df ${DF}/his_unsep_txt_all_df.p -of ${CLASS_VEC}/his_unsep_norm_class_vectors.p -n

echo
echo "Classification..."
echo "================================"

echo "Single unnormed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_his_instances.p -ci ${CLASS_VEC}/his_unsep_unnorm_class_vectors.p -of ${CLASS_OUT}/his_unsep_unnorm_single_class.txt -m single -mf ${RESULTS}
echo
echo "Single normed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_his_instances.p -ci ${CLASS_VEC}/his_unsep_norm_class_vectors.p -of ${CLASS_OUT}/his_unsep_norm_single_class.txt -m single -mf ${RESULTS}

echo
echo "--"

echo
echo "Cascade unnormed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_his_instances.p -ci ${CLASS_VEC}/his_unsep_unnorm_class_vectors.p -of ${CLASS_OUT}/his_unsep_unnorm_cascade_class.txt -m cascade -mf ${RESULTS}
echo
echo "Cascade normed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_his_instances.p -ci ${CLASS_VEC}/his_unsep_norm_class_vectors.p -of ${CLASS_OUT}/his_unsep_norm_cascade_class.txt -m cascade -mf ${RESULTS}
