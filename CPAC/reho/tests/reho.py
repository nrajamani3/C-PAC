@raises(ValueError)
def test_cluster_size_raise_exception():
    #cluster size has to be in [7, 19, 27]
    #raise value error if user pass wrong value
    wf = create_reho_wf()
    wf.in_file = ''
    wf.mask = ''
    wf.cluster_size = 1
    wf.run()

def test_cluster_size():
    #does not raise exception if cluster size is accepted value
    wf = create_reho_wf()
    wf.in_file = ''
    wf.mask = ''
    wf.cluster_size = 27
    wf.run()
    assert True


def test_output_is_nii():
    #test if output exist after running the wf
    #and is nifti file

    wf = create_reho_wf()
    wf.in_file = ''
    wf.mask = ''
    wf.cluster_size = 7
    wf.run()

    out = wf.outputspec.out_file
    assert out.endswith('.nii.gz')


def test_output_shape():
    #test if the output file has the same shape as the input file
    #but is 3d instead of 4d
    infile = ''
    after = nb.load(infile).shape

    wf = create_reho_wf()
    wf.in_file = infile
    wf.mask = ''
    wf.cluster_size = 7
    wf.run()

    out = wf.outputspec.out_file
    before = nb.load(out).shape

    #file stil has the same shape
    assert after[:3] == before[:3]

    #and it is a 3d file
    assert before[3] == 3
