# python panta.py -p init -g /data/hoan/amromics/data/prokka_output/*/*.gff -o ../pan-genome/examples/test/output -as -s
# python panta.py -p init -g examples/test/init/*.gff.gz -o ../pan-genome/examples/test/output -as -s
# python panta.py -p init -g /data/hoan/amromics/data/ncbi/complete/*.gff.gz -o ../pan-genome/examples/test/output -as -s
# python panta.py -p init -a /data/hoan/amromics/data/ncbi/complete/*.fna.gz -o ../pan-genome/examples/test/output -as -s
# python panta.py -p init -a ../data/g_contig/*.fna.gz -o ../pan-genome/examples/test/output -as -s
# python panta.py -p init -a ../data/ncbi/complete/*.fna.gz -o ../genome-graph/examples/test/output -as -s
# python panta.py -p init -a ../data/ncbi/complete/*.fna.gz -o examples/test/output -as -s
# python panta.py -p add -a ../data/ncbi/incomplete/*.fna.gz -o examples/test/output_Kp30 -as -s
# python panta.py -p init -g ../data/ncbi/Kp30_plus1/*.gff.gz -o examples/test/output_Kp30plus1 -as -s
# python panta.py -p init -a ../data/ncbi/Kp30_plus1/*.fna.gz -o examples/test/output_Kp30plus1 -as -s
python panta.py -p init -a ../data/ncbi/Kp100random/*.fna.gz -o examples/test/output_Kp100 -as -s
