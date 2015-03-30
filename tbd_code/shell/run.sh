# sh run.sh configure.ini
shdir=$(dirname $(readlink -f ${BASH_SOURCE[0]}))

#configure=$shdir/conf/configure.ini
configure=$1
python="PYTHON PATH"

disable_caltrainfeaturelabel=1
disable_calvalfeaturelabel=1
disable_caltestfeature=1
disable_training=1
disable_evaluation=1
disable_submisssion=1

if [ "$disable_caltrainfeaturelabel" != "1" ]; then
    echo "calculate training feature and label..." 1>&2
    $python $shdir/../extractor/featureextractor.py calfeatures train $configure
    $python $shdir/../extractor/featureextractor.py callabels train $configure
    $python $shdir/../extractor/featureextractor.py calcombine train $configure
else
    echo "calculate training feature and label disabled!"
fi

if [ "$disable_calvalfeaturelabel" != "1" ]; then
    echo "calculate validation feature and label..." 1>&2
    $python $shdir/../extractor/featureextractor.py calfeatures val $configure
    $python $shdir/../extractor/featureextractor.py callabels val $configure
    $python $shdir/../extractor/featureextractor.py calcombine val $configure
else
    echo "calculate validation feature and label disabled!"
fi

if [ "$disable_caltestfeature" != "1" ]; then
    echo "calculate testing feature..." 1>&2
    $python $shdir/../extractor/featureextractor.py calfeatures test $configure
else
    echo "calculate testing feature and label disabled!"
fi

if [ "$disable_training" != "1" ]; then
    echo "training..." 1>&2
    $python $shdir/../extractor/featureextractor.py train train $configure
else
    echo "training disabled!"
fi

if [ "$disable_evaluation" != "1" ]; then
    echo "evaluation..." 1>&2
    $python $shdir/../extractor/featureextractor.py evaluate val $configure
    $python $shdir/../extractor/featureextractor.py evaluate test $configure
else
    echo "evaluation disabled!"
fi

if [ "$disable_submisssion" != "1" ]; then
    echo "submission..." 1>&2
    $python $shdir/../extractor/featureextractor.py submit test $configure
else
    echo "submission disabled!"
fi
