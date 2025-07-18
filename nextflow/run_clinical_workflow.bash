
nextflow -C nextflow.config run ardac_etl_workflow.nf -profile conda,workstation -with-trace -with-timeline ardac_etl_timeline.html --subjects_type clinical

