CLASS_OUT="classifier_output"
INST_VEC="instance_vectors"
CLASS_VEC="class_vectors"
RESULTS="classification_results.txt"
DATA="/home/kedz/data/disaster_wikis"
DF="doc_freqs"


echo "### 1A) Running Abstract Separated ###"
echo "======================================"

echo
echo "Building document frequencies..."
echo "================================"
python docfreq.py -id ${DATA}/xml_sep/abstract_text -of ${DF}/abs_sep_txt_all_df.p

echo
echo "Building instance vectors..."
echo "================================"
python create_instance_vectors.py -id ${DATA}/linked_pages_xml/ -df doc_freqs/abs_sep_txt_all_df.p -of ${INST_VEC}/linked_pages_abs_instances.p

echo
echo "Building class vectors..."
echo "================================"
echo "Creating unnormed class vectors..."
python create_class_vectors.py -id ${DATA}/xml_sep/abstract_text/ -df ${DF}/abs_sep_txt_all_df.p -of ${CLASS_VEC}/abs_sep_unnorm_class_vectors.p
echo "Creating normed class vectors..."
python create_class_vectors.py -id ${DATA}/xml_sep/abstract_text/ -df ${DF}/abs_sep_txt_all_df.p -of ${CLASS_VEC}/abs_sep_norm_class_vectors.p -n

echo
echo "Classification..."
echo "================================"

echo "Single unnormed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_abs_instances.p -ci ${CLASS_VEC}/abs_sep_unnorm_class_vectors.p -of ${CLASS_OUT}/abs_sep_unnorm_single_class.txt -m single -mf ${RESULTS}
echo "Single normed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_abs_instances.p -ci ${CLASS_VEC}/abs_sep_norm_class_vectors.p -of ${CLASS_OUT}/abs_sep_norm_single_class.txt -m single -mf ${RESULTS}

echo "Cascade unnormed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_abs_instances.p -ci ${CLASS_VEC}/abs_sep_unnorm_class_vectors.p -of ${CLASS_OUT}/abs_sep_unnorm_cascade_class.txt -m cascade -mf ${RESULTS}
echo "Cascade normed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_abs_instances.p -ci ${CLASS_VEC}/abs_sep_norm_class_vectors.p -of ${CLASS_OUT}/abs_sep_norm_cascade_class.txt -m cascade -mf ${RESULTS}


echo
echo "### 1B) Running Impact Separated   ###"
echo "======================================"

echo
echo "Building document frequencies..."
echo "================================"
python docfreq.py -id ${DATA}/xml_sep/impact_text -of ${DF}/imp_sep_txt_all_df.p

echo
echo "Building instance vectors..."
echo "================================"
python create_instance_vectors.py -id ${DATA}/linked_pages_xml/ -df doc_freqs/imp_sep_txt_all_df.p -of ${INST_VEC}/linked_pages_imp_instances.p

echo
echo "Building class vectors..."
echo "================================"
echo "Creating unnormed class vectors..."
python create_class_vectors.py -id ${DATA}/xml_sep/impact_text/ -df ${DF}/imp_sep_txt_all_df.p -of ${CLASS_VEC}/imp_sep_unnorm_class_vectors.p
echo "Creating normed class vectors..."
python create_class_vectors.py -id ${DATA}/xml_sep/impact_text/ -df ${DF}/imp_sep_txt_all_df.p -of ${CLASS_VEC}/imp_sep_norm_class_vectors.p -n

echo
echo "Classification..."
echo "================================"

echo "Single unnormed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_imp_instances.p -ci ${CLASS_VEC}/imp_sep_unnorm_class_vectors.p -of ${CLASS_OUT}/imp_sep_unnorm_single_class.txt -m single -mf ${RESULTS}
echo "Single normed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_imp_instances.p -ci ${CLASS_VEC}/imp_sep_norm_class_vectors.p -of ${CLASS_OUT}/imp_sep_norm_single_class.txt -m single -mf ${RESULTS}

echo "Cascade unnormed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_imp_instances.p -ci ${CLASS_VEC}/imp_sep_unnorm_class_vectors.p -of ${CLASS_OUT}/imp_sep_unnorm_cascade_class.txt -m cascade -mf ${RESULTS}
echo "Cascade normed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_imp_instances.p -ci ${CLASS_VEC}/imp_sep_norm_class_vectors.p -of ${CLASS_OUT}/imp_sep_norm_cascade_class.txt -m cascade -mf ${RESULTS}



echo
echo "### 1C) Running History Separated  ###"
echo "======================================"

echo
echo "Building document frequencies..."
echo "================================"
python docfreq.py -id ${DATA}/xml_sep/history_text -of ${DF}/his_sep_txt_all_df.p

echo
echo "Building instance vectors..."
echo "================================"
python create_instance_vectors.py -id ${DATA}/linked_pages_xml/ -df doc_freqs/his_sep_txt_all_df.p -of ${INST_VEC}/linked_pages_his_instances.p

echo
echo "Building class vectors..."
echo "================================"
echo "Creating unnormed class vectors..."
python create_class_vectors.py -id ${DATA}/xml_sep/history_text/ -df ${DF}/his_sep_txt_all_df.p -of ${CLASS_VEC}/his_sep_unnorm_class_vectors.p
echo "Creating normed class vectors..."
python create_class_vectors.py -id ${DATA}/xml_sep/history_text/ -df ${DF}/his_sep_txt_all_df.p -of ${CLASS_VEC}/his_sep_norm_class_vectors.p -n

echo
echo "Classification..."
echo "================================"

echo "Single unnormed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_his_instances.p -ci ${CLASS_VEC}/his_sep_unnorm_class_vectors.p -of ${CLASS_OUT}/his_sep_unnorm_single_class.txt -m single -mf ${RESULTS}
echo "Single normed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_his_instances.p -ci ${CLASS_VEC}/his_sep_norm_class_vectors.p -of ${CLASS_OUT}/his_sep_norm_single_class.txt -m single -mf ${RESULTS}

echo "Cascade unnormed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_his_instances.p -ci ${CLASS_VEC}/his_sep_unnorm_class_vectors.p -of ${CLASS_OUT}/his_sep_unnorm_cascade_class.txt -m cascade -mf ${RESULTS}
echo "Cascade normed..."
python nearestneighbors.py -ti ${INST_VEC}/linked_pages_his_instances.p -ci ${CLASS_VEC}/his_sep_norm_class_vectors.p -of ${CLASS_OUT}/his_sep_norm_cascade_class.txt -m cascade -mf ${RESULTS}
