(lp0
(lp1
S'alff_collect_transforms_0'
p2
aS'alff_to_standard_0'
p3
aS"[('outputspec.transformation_series', 'inputspec.transforms')]"
p4
aa(lp5
S'alff_falff_0'
p6
aS'alff_fsl_to_itk_0'
p7
aS"[('outputspec.alff_img', 'inputspec.source_file')]"
p8
aa(lp9
g6
aS'alff_smooth_0'
p10
aS"[('outputspec.alff_img', 'in_file')]"
p11
aa(lp12
g6
ag3
aS"[('outputspec.alff_img', 'inputspec.input_image')]"
p13
aa(lp14
g6
aS'falff_fsl_to_itk_1'
p15
aS"[('outputspec.falff_img', 'inputspec.source_file')]"
p16
aa(lp17
g6
aS'falff_smooth_1'
p18
aS"[('outputspec.falff_img', 'in_file')]"
p19
aa(lp20
g6
aS'falff_to_standard_1'
p21
aS"[('outputspec.falff_img', 'inputspec.input_image')]"
p22
aa(lp23
g6
aS'log_alff_falff_0'
p24
aS"[('outputspec.falff_img', 'inputspec.inputs')]"
p25
aa(lp26
g7
ag2
aS"[('outputspec.itk_transform', 'inputspec.fsl_to_itk_affine')]"
p27
aa(lp28
g10
aS'alff_smooth_mean_0'
p29
aS"[('out_file', 'in_file')]"
p30
aa(lp31
g29
aS'alff_smooth_mean_to_txt_0'
p32
aS"[('out_file', 'in_file')]"
p33
aa(lp34
g3
aS'alff_to_standard_smooth_0'
p35
aS"[('outputspec.output_image', 'in_file')]"
p36
aa(lp37
g35
aS'alff_to_standard_smooth_mean_0'
p38
aS"[('out_file', 'in_file')]"
p39
aa(lp40
g35
aS'dp_alff_1'
p41
aS"[('out_file', 'measure_file')]"
p42
aa(lp43
g35
aS'hist_alff_1'
p44
aS"[('out_file', 'measure_file')]"
p45
aa(lp46
g35
aS'log_alff_to_standard_smooth_0'
p47
aS"[('out_file', 'inputspec.inputs')]"
p48
aa(lp49
g35
aS'z_score_std_alff_0'
p50
aS"[('out_file', 'inputspec.input_file')]"
p51
aa(lp52
g38
aS'alff_to_standard_smooth_mean_to_txt_0'
p53
aS"[('out_file', 'in_file')]"
p54
aa(lp55
S'anat_edge_1'
p56
aS'montage_anat_1'
p57
aS"[('new_fname', 'inputspec.overlay')]"
p58
aa(lp59
S'anat_gather_0'
p60
aS'anat_preproc_0'
p61
aS"[('outputspec.anat', 'inputspec.anat')]"
p62
aa(lp63
S'anat_mni_ants_register_0'
p64
ag2
aS"[('outputspec.warp_field', 'inputspec.warp_file'), ('outputspec.ants_initial_xfm', 'inputspec.linear_initial'), ('outputspec.ants_affine_xfm', 'inputspec.linear_affine'), ('outputspec.ants_rigid_xfm', 'inputspec.linear_rigid')]"
p65
aa(lp66
g64
aS'collect_transforms_functional_brain_mask_to_standard_0'
p67
aS"[('outputspec.warp_field', 'inputspec.warp_file'), ('outputspec.ants_initial_xfm', 'inputspec.linear_initial'), ('outputspec.ants_affine_xfm', 'inputspec.linear_affine'), ('outputspec.ants_rigid_xfm', 'inputspec.linear_rigid')]"
p68
aa(lp69
g64
aS'collect_transforms_functional_mni_0'
p70
aS"[('outputspec.warp_field', 'inputspec.warp_file'), ('outputspec.ants_initial_xfm', 'inputspec.linear_initial'), ('outputspec.ants_affine_xfm', 'inputspec.linear_affine'), ('outputspec.ants_rigid_xfm', 'inputspec.linear_rigid')]"
p71
aa(lp72
g64
aS'collect_transforms_mean_functional_in_mni_0'
p73
aS"[('outputspec.warp_field', 'inputspec.warp_file'), ('outputspec.ants_initial_xfm', 'inputspec.linear_initial'), ('outputspec.ants_affine_xfm', 'inputspec.linear_affine'), ('outputspec.ants_rigid_xfm', 'inputspec.linear_rigid')]"
p74
aa(lp75
g64
aS'dr_tempreg_maps_files_collect_transforms_2'
p76
aS"[('outputspec.warp_field', 'inputspec.warp_file'), ('outputspec.ants_initial_xfm', 'inputspec.linear_initial'), ('outputspec.ants_affine_xfm', 'inputspec.linear_affine'), ('outputspec.ants_rigid_xfm', 'inputspec.linear_rigid')]"
p77
aa(lp78
g64
aS'dr_tempreg_maps_stack_collect_transforms_0'
p79
aS"[('outputspec.warp_field', 'inputspec.warp_file'), ('outputspec.ants_initial_xfm', 'inputspec.linear_initial'), ('outputspec.ants_affine_xfm', 'inputspec.linear_affine'), ('outputspec.ants_rigid_xfm', 'inputspec.linear_rigid')]"
p80
aa(lp81
g64
aS'dr_tempreg_maps_zstat_files_collect_transforms_3'
p82
aS"[('outputspec.warp_field', 'inputspec.warp_file'), ('outputspec.ants_initial_xfm', 'inputspec.linear_initial'), ('outputspec.ants_affine_xfm', 'inputspec.linear_affine'), ('outputspec.ants_rigid_xfm', 'inputspec.linear_rigid')]"
p83
aa(lp84
g64
aS'dr_tempreg_maps_zstat_stack_collect_transforms_1'
p85
aS"[('outputspec.warp_field', 'inputspec.warp_file'), ('outputspec.ants_initial_xfm', 'inputspec.linear_initial'), ('outputspec.ants_affine_xfm', 'inputspec.linear_affine'), ('outputspec.ants_rigid_xfm', 'inputspec.linear_rigid')]"
p86
aa(lp87
g64
aS'falff_collect_transforms_1'
p88
aS"[('outputspec.warp_field', 'inputspec.warp_file'), ('outputspec.ants_initial_xfm', 'inputspec.linear_initial'), ('outputspec.ants_affine_xfm', 'inputspec.linear_affine'), ('outputspec.ants_rigid_xfm', 'inputspec.linear_rigid')]"
p89
aa(lp90
g64
aS'log_anat_mni_ants_register_0'
p91
aS"[('outputspec.normalized_output_brain', 'inputspec.inputs')]"
p92
aa(lp93
g64
aS'montage_mni_anat_1'
p94
aS"[('outputspec.normalized_output_brain', 'inputspec.underlay')]"
p95
aa(lp96
g64
aS'nuisance_0'
p97
aS"[('outputspec.ants_initial_xfm', 'inputspec.anat_to_mni_initial_xfm'), ('outputspec.ants_rigid_xfm', 'inputspec.anat_to_mni_rigid_xfm'), ('outputspec.ants_affine_xfm', 'inputspec.anat_to_mni_affine_xfm')]"
p98
aa(lp99
g64
aS'reho_collect_transforms_0'
p100
aS"[('outputspec.warp_field', 'inputspec.warp_file'), ('outputspec.ants_initial_xfm', 'inputspec.linear_initial'), ('outputspec.ants_affine_xfm', 'inputspec.linear_affine'), ('outputspec.ants_rigid_xfm', 'inputspec.linear_rigid')]"
p101
aa(lp102
g64
aS'sca_roi_collect_transforms_0'
p103
aS"[('outputspec.warp_field', 'inputspec.warp_file'), ('outputspec.ants_initial_xfm', 'inputspec.linear_initial'), ('outputspec.ants_affine_xfm', 'inputspec.linear_affine'), ('outputspec.ants_rigid_xfm', 'inputspec.linear_rigid')]"
p104
aa(lp105
g64
aS'sca_seed_collect_transforms_0'
p106
aS"[('outputspec.warp_field', 'inputspec.warp_file'), ('outputspec.ants_initial_xfm', 'inputspec.linear_initial'), ('outputspec.ants_affine_xfm', 'inputspec.linear_affine'), ('outputspec.ants_rigid_xfm', 'inputspec.linear_rigid')]"
p107
aa(lp108
g64
aS'seg_preproc_0'
p109
aS"[('outputspec.ants_affine_xfm', 'inputspec.standard2highres_mat'), ('outputspec.ants_rigid_xfm', 'inputspec.standard2highres_rig')]"
p110
aa(lp111
g61
ag7
aS"[('outputspec.brain', 'inputspec.reference_file')]"
p112
aa(lp113
g61
ag56
aS"[('outputspec.brain', 'file_')]"
p114
aa(lp115
g61
ag64
aS"[('outputspec.brain', 'inputspec.anatomical_brain')]"
p116
aa(lp117
g61
aS'dr_tempreg_maps_files_fsl_to_itk_2'
p118
aS"[('outputspec.brain', 'inputspec.reference_file')]"
p119
aa(lp120
g61
aS'dr_tempreg_maps_stack_fsl_to_itk_0'
p121
aS"[('outputspec.brain', 'inputspec.reference_file')]"
p122
aa(lp123
g61
aS'dr_tempreg_maps_zstat_files_fsl_to_itk_3'
p124
aS"[('outputspec.brain', 'inputspec.reference_file')]"
p125
aa(lp126
g61
aS'dr_tempreg_maps_zstat_stack_fsl_to_itk_1'
p127
aS"[('outputspec.brain', 'inputspec.reference_file')]"
p128
aa(lp129
g61
ag15
aS"[('outputspec.brain', 'inputspec.reference_file')]"
p130
aa(lp131
g61
aS'fsl_to_itk_functional_brain_mask_to_standard_0'
p132
aS"[('outputspec.brain', 'inputspec.reference_file')]"
p133
aa(lp134
g61
aS'fsl_to_itk_functional_mni_0'
p135
aS"[('outputspec.brain', 'inputspec.reference_file')]"
p136
aa(lp137
g61
aS'fsl_to_itk_mean_functional_in_mni_0'
p138
aS"[('outputspec.brain', 'inputspec.reference_file')]"
p139
aa(lp140
g61
aS'func_to_anat_FLIRT_0'
p141
aS"[('outputspec.brain', 'inputspec.anat')]"
p142
aa(lp143
g61
aS'func_to_anat_bbreg_0'
p144
aS"[('outputspec.reorient', 'inputspec.anat_skull')]"
p145
aa(lp146
g61
aS'log_anat_preproc_0'
p147
aS"[('outputspec.brain', 'inputspec.inputs')]"
p148
aa(lp149
g61
aS'montage_csf_gm_wm_1'
p150
aS"[('outputspec.brain', 'inputspec.underlay')]"
p151
aa(lp152
g61
aS'montage_skull_1'
p153
aS"[('outputspec.brain', 'inputspec.underlay')]"
p154
aa(lp155
g61
aS'montage_snr_1'
p156
aS"[('outputspec.brain', 'inputspec.underlay')]"
p157
aa(lp158
g61
aS'reho_fsl_to_itk_0'
p159
aS"[('outputspec.brain', 'inputspec.reference_file')]"
p160
aa(lp161
g61
aS'sca_roi_fsl_to_itk_0'
p162
aS"[('outputspec.brain', 'inputspec.reference_file')]"
p163
aa(lp164
g61
aS'sca_seed_fsl_to_itk_0'
p165
aS"[('outputspec.brain', 'inputspec.reference_file')]"
p166
aa(lp167
g61
ag109
aS"[('outputspec.brain', 'inputspec.brain')]"
p168
aa(lp169
g61
aS'skull_edge_1'
p170
aS"[('outputspec.reorient', 'file_')]"
p171
aa(lp172
g61
aS'std_dev_anat_1'
p173
aS"[('outputspec.brain', 'ref_')]"
p174
aa(lp175
g61
aS'vmhc_0'
p176
aS"[('outputspec.brain', 'inputspec.brain'), ('outputspec.reorient', 'inputspec.reorient')]"
p177
aa(lp178
S'apply_ants_warp_functional_brain_mask_to_standard_0'
p179
ag35
aS"[('outputspec.output_image', 'operand_files')]"
p180
aa(lp181
g179
aS'dr_tempreg_maps_Z_files_smooth_0'
p182
aS"[('outputspec.output_image', 'operand_files')]"
p183
aa(lp184
g179
aS'dr_tempreg_maps_Z_stack_smooth_0'
p185
aS"[('outputspec.output_image', 'operand_files')]"
p186
aa(lp187
g179
aS'dr_tempreg_maps_files_smooth_0'
p188
aS"[('outputspec.output_image', 'operand_files')]"
p189
aa(lp190
g179
aS'dr_tempreg_maps_stack_smooth_0'
p191
aS"[('outputspec.output_image', 'operand_files')]"
p192
aa(lp193
g179
aS'falff_to_standard_smooth_1'
p194
aS"[('outputspec.output_image', 'operand_files')]"
p195
aa(lp196
g179
aS'log_apply_ants_warp_functional_brain_mask_to_standard_0'
p197
aS"[('outputspec.output_image', 'inputspec.inputs')]"
p198
aa(lp199
g179
aS'reho_to_standard_smooth_0'
p200
aS"[('outputspec.output_image', 'operand_files')]"
p201
aa(lp202
g179
aS'sca_roi_to_standard_smooth_0'
p203
aS"[('outputspec.output_image', 'operand_files')]"
p204
aa(lp205
g179
aS'sca_seed_to_standard_smooth_0'
p206
aS"[('outputspec.output_image', 'operand_files')]"
p207
aa(lp208
g179
aS'sca_tempreg_maps_Z_files_smooth_0'
p209
aS"[('outputspec.output_image', 'operand_files')]"
p210
aa(lp211
g179
aS'sca_tempreg_maps_Z_stack_smooth_0'
p212
aS"[('outputspec.output_image', 'operand_files')]"
p213
aa(lp214
g179
aS'sca_tempreg_maps_files_smooth_0'
p215
aS"[('outputspec.output_image', 'operand_files')]"
p216
aa(lp217
g179
aS'sca_tempreg_maps_stack_smooth_0'
p218
aS"[('outputspec.output_image', 'operand_files')]"
p219
aa(lp220
g179
aS'spatial_map_timeseries_0'
p221
aS"[('outputspec.output_image', 'inputspec.subject_mask')]"
p222
aa(lp223
g179
aS'temporal_regression_sca_0'
p224
aS"[('outputspec.output_image', 'inputspec.subject_mask')]"
p225
aa(lp226
g179
ag50
aS"[('outputspec.output_image', 'inputspec.mask_file')]"
p227
aa(lp228
g179
aS'z_score_std_falff_0'
p229
aS"[('outputspec.output_image', 'inputspec.mask_file')]"
p230
aa(lp231
g179
aS'z_score_std_reho_0'
p232
aS"[('outputspec.output_image', 'inputspec.mask_file')]"
p233
aa(lp234
S'apply_ants_warp_functional_mni_0'
p235
aS'log_apply_ants_warp_functional_mni_0'
p236
aS"[('outputspec.output_image', 'inputspec.inputs')]"
p237
aa(lp238
g235
aS'resample_functional_to_mask_0'
p239
aS"[('outputspec.output_image', 'in_file')]"
p240
aa(lp241
g235
aS'resample_functional_to_mask_for_sca_0'
p242
aS"[('outputspec.output_image', 'in_file')]"
p243
aa(lp244
g235
aS'resample_functional_to_roi_0'
p245
aS"[('outputspec.output_image', 'in_file')]"
p246
aa(lp247
g235
aS'resample_functional_to_roi_for_sca_0'
p248
aS"[('outputspec.output_image', 'in_file')]"
p249
aa(lp250
g235
aS'resample_spatial_map_to_native_space_0'
p251
aS"[('outputspec.output_image', 'reference')]"
p252
aa(lp253
g235
ag221
aS"[('outputspec.output_image', 'inputspec.subject_rest')]"
p254
aa(lp255
g235
ag224
aS"[('outputspec.output_image', 'inputspec.subject_rest')]"
p256
aa(lp257
S'apply_ants_warp_mean_functional_in_mni_0'
p258
aS'log_apply_ants_warp_mean_functional_in_mni_0'
p259
aS"[('outputspec.output_image', 'inputspec.inputs')]"
p260
aa(lp261
g258
aS'montage_mfi_1'
p262
aS"[('outputspec.output_image', 'inputspec.underlay')]"
p263
aa(lp264
g67
ag179
aS"[('outputspec.transformation_series', 'inputspec.transforms')]"
p265
aa(lp266
g67
aS'log_collect_transforms_functional_brain_mask_to_standard_0'
p267
aS"[('outputspec.transformation_series', 'inputspec.inputs')]"
p268
aa(lp269
g70
ag235
aS"[('outputspec.transformation_series', 'inputspec.transforms')]"
p270
aa(lp271
g70
aS'log_collect_transforms_functional_mni_0'
p272
aS"[('outputspec.transformation_series', 'inputspec.inputs')]"
p273
aa(lp274
g73
ag258
aS"[('outputspec.transformation_series', 'inputspec.transforms')]"
p275
aa(lp276
g73
aS'log_collect_transforms_mean_functional_in_mni_0'
p277
aS"[('outputspec.transformation_series', 'inputspec.inputs')]"
p278
aa(lp279
g41
aS'montage_alff_1'
p280
aS"[('modified_measure_file', 'inputspec.overlay')]"
p281
aa(lp282
S'dp_alff_zstd_1'
p283
aS'montage_alff_zstd_1'
p284
aS"[('modified_measure_file', 'inputspec.overlay')]"
p285
aa(lp286
S'dp_falff_1'
p287
aS'montage_falff_1'
p288
aS"[('modified_measure_file', 'inputspec.overlay')]"
p289
aa(lp290
S'dp_falff_zstd_1'
p291
aS'montage_falff_zstd_1'
p292
aS"[('modified_measure_file', 'inputspec.overlay')]"
p293
aa(lp294
S'dp_reho_1'
p295
aS'montage_reho_1'
p296
aS"[('modified_measure_file', 'inputspec.overlay')]"
p297
aa(lp298
S'dp_reho_zstd_1'
p299
aS'montage_reho_zstd_1'
p300
aS"[('modified_measure_file', 'inputspec.overlay')]"
p301
aa(lp302
S'dp_snr_1'
p303
ag156
aS"[('modified_measure_file', 'inputspec.overlay')]"
p304
aa(lp305
S'dp_temporal_dual_regression_1'
p306
aS'montage_temporal_dual_regression_1'
p307
aS"[('modified_measure_file', 'inputspec.overlay')]"
p308
aa(lp309
S'dp_temporal_regression_sca_1'
p310
aS'montage_temporal_regression_sca_1'
p311
aS"[('modified_measure_file', 'inputspec.overlay')]"
p312
aa(lp313
S'dp_vmhc1'
p314
aS'montage_vmhc_1'
p315
aS"[('modified_measure_file', 'inputspec.overlay')]"
p316
aa(lp317
g182
ag306
aS"[('out_file', 'measure_file')]"
p318
aa(lp319
g182
aS'hist_temp_dr_1'
p320
aS"[('out_file', 'measure_file')]"
p321
aa(lp322
g76
aS'dr_tempreg_maps_files_to_standard_2'
p323
aS"[('outputspec.transformation_series', 'inputspec.transforms')]"
p324
aa(lp325
g118
ag76
aS"[('outputspec.itk_transform', 'inputspec.fsl_to_itk_affine')]"
p326
aa(lp327
g323
ag188
aS"[('outputspec.output_image', 'in_file')]"
p328
aa(lp329
g79
aS'dr_tempreg_maps_stack_to_standard_0'
p330
aS"[('outputspec.transformation_series', 'inputspec.transforms')]"
p331
aa(lp332
g121
ag79
aS"[('outputspec.itk_transform', 'inputspec.fsl_to_itk_affine')]"
p333
aa(lp334
g191
aS'log_dr_tempreg_maps_stack_smooth_0'
p335
aS"[('out_file', 'inputspec.inputs')]"
p336
aa(lp337
g330
ag191
aS"[('outputspec.output_image', 'in_file')]"
p338
aa(lp339
g82
aS'dr_tempreg_maps_zstat_files_to_standard_3'
p340
aS"[('outputspec.transformation_series', 'inputspec.transforms')]"
p341
aa(lp342
g124
ag82
aS"[('outputspec.itk_transform', 'inputspec.fsl_to_itk_affine')]"
p343
aa(lp344
g340
ag182
aS"[('outputspec.output_image', 'in_file')]"
p345
aa(lp346
g85
aS'dr_tempreg_maps_zstat_stack_to_standard_1'
p347
aS"[('outputspec.transformation_series', 'inputspec.transforms')]"
p348
aa(lp349
g127
ag85
aS"[('outputspec.itk_transform', 'inputspec.fsl_to_itk_affine')]"
p350
aa(lp351
g347
ag185
aS"[('outputspec.output_image', 'in_file')]"
p352
aa(lp353
S'edit_func_0'
p354
aS'func_preproc_automask_0'
p355
aS"[('outputspec.edited_func', 'inputspec.func')]"
p356
aa(lp357
g88
ag21
aS"[('outputspec.transformation_series', 'inputspec.transforms')]"
p358
aa(lp359
g15
ag88
aS"[('outputspec.itk_transform', 'inputspec.fsl_to_itk_affine')]"
p360
aa(lp361
g18
aS'falff_smooth_mean_1'
p362
aS"[('out_file', 'in_file')]"
p363
aa(lp364
g362
aS'falff_smooth_mean_to_txt_1'
p365
aS"[('out_file', 'in_file')]"
p366
aa(lp367
g21
ag194
aS"[('outputspec.output_image', 'in_file')]"
p368
aa(lp369
g194
ag287
aS"[('out_file', 'measure_file')]"
p370
aa(lp371
g194
aS'falff_to_standard_smooth_mean_1'
p372
aS"[('out_file', 'in_file')]"
p373
aa(lp374
g194
aS'hist_falff_1'
p375
aS"[('out_file', 'measure_file')]"
p376
aa(lp377
g194
aS'log_falff_to_standard_smooth_1'
p378
aS"[('out_file', 'inputspec.inputs')]"
p379
aa(lp380
g194
ag229
aS"[('out_file', 'inputspec.input_file')]"
p381
aa(lp382
g372
aS'falff_to_standard_smooth_mean_to_txt_1'
p383
aS"[('out_file', 'in_file')]"
p384
aa(lp385
S'frequency_filter_0'
p386
ag235
aS"[('bandpassed_file', 'inputspec.input_image')]"
p387
aa(lp388
g386
aS'log_frequency_filter_0'
p389
aS"[('bandpassed_file', 'inputspec.inputs')]"
p390
aa(lp391
g386
aS'reho_0'
p392
aS"[('bandpassed_file', 'inputspec.rest_res_filt')]"
p393
aa(lp394
g386
aS'sca_roi_0'
p395
aS"[('bandpassed_file', 'inputspec.functional_file')]"
p396
aa(lp397
g386
aS'sca_seed_0'
p398
aS"[('bandpassed_file', 'inputspec.functional_file')]"
p399
aa(lp400
g386
aS'temporal_dual_regression_0'
p401
aS"[('bandpassed_file', 'inputspec.subject_rest')]"
p402
aa(lp403
g386
ag176
aS"[('bandpassed_file', 'inputspec.rest_res')]"
p404
aa(lp405
S'fristons_parameter_model_0'
p406
aS'gen_motion_stats_0'
p407
aS"[('outputspec.movement_file', 'inputspec.movement_parameters')]"
p408
aa(lp409
g406
aS'log_fristons_parameter_model_0'
p410
aS"[('outputspec.movement_file', 'inputspec.inputs')]"
p411
aa(lp412
g406
aS'motion_plt_1'
p413
aS"[('outputspec.movement_file', 'motion_parameters')]"
p414
aa(lp415
g406
ag97
aS"[('outputspec.movement_file', 'inputspec.motion_components')]"
p416
aa(lp417
g132
ag67
aS"[('outputspec.itk_transform', 'inputspec.fsl_to_itk_affine')]"
p418
aa(lp419
g132
aS'log_fsl_to_itk_functional_brain_mask_to_standard_0'
p420
aS"[('outputspec.itk_transform', 'inputspec.inputs')]"
p421
aa(lp422
g135
ag70
aS"[('outputspec.itk_transform', 'inputspec.fsl_to_itk_affine')]"
p423
aa(lp424
g135
aS'log_fsl_to_itk_functional_mni_0'
p425
aS"[('outputspec.itk_transform', 'inputspec.inputs')]"
p426
aa(lp427
g138
ag73
aS"[('outputspec.itk_transform', 'inputspec.fsl_to_itk_affine')]"
p428
aa(lp429
g138
aS'log_fsl_to_itk_mean_functional_in_mni_0'
p430
aS"[('outputspec.itk_transform', 'inputspec.inputs')]"
p431
aa(lp432
S'func_gather_0'
p433
ag354
aS"[('outputspec.rest', 'inputspec.func')]"
p434
aa(lp435
g433
ag407
aS"[('outputspec.subject', 'inputspec.subject_id'), ('outputspec.scan', 'inputspec.scan_id')]"
p436
aa(lp437
g433
aS'scan_params_0'
p438
aS"[('outputspec.subject', 'subject'), ('outputspec.scan', 'scan')]"
p439
aa(lp440
g355
ag6
aS"[('outputspec.mask', 'inputspec.rest_mask')]"
p441
aa(lp442
g355
ag10
aS"[('outputspec.mask', 'operand_files')]"
p443
aa(lp444
g355
ag179
aS"[('outputspec.mask', 'inputspec.input_image')]"
p445
aa(lp446
g355
ag258
aS"[('outputspec.example_func', 'inputspec.input_image')]"
p447
aa(lp448
g355
ag18
aS"[('outputspec.mask', 'operand_files')]"
p449
aa(lp450
g355
ag406
aS"[('outputspec.movement_parameters', 'inputspec.movement_file')]"
p451
aa(lp452
g355
ag132
aS"[('outputspec.mask', 'inputspec.source_file')]"
p453
aa(lp454
g355
ag135
aS"[('outputspec.example_func', 'inputspec.source_file')]"
p455
aa(lp456
g355
ag138
aS"[('outputspec.example_func', 'inputspec.source_file')]"
p457
aa(lp458
g355
ag141
aS"[('outputspec.example_func', 'inputspec.func')]"
p459
aa(lp460
g355
ag144
aS"[('outputspec.example_func', 'inputspec.func')]"
p461
aa(lp462
g355
ag407
aS"[('outputspec.motion_correct', 'inputspec.motion_correct'), ('outputspec.max_displacement', 'inputspec.max_displacement'), ('outputspec.mask', 'inputspec.mask'), ('outputspec.oned_matrix_save', 'inputspec.oned_matrix_save')]"
p463
aa(lp464
g355
aS'log_func_preproc_automask_0'
p465
aS"[('outputspec.preprocessed', 'inputspec.inputs')]"
p466
aa(lp467
g355
ag97
aS"[('outputspec.preprocessed', 'inputspec.subject')]"
p468
aa(lp469
g355
ag392
aS"[('outputspec.mask', 'inputspec.rest_mask')]"
p470
aa(lp471
g355
aS'reho_smooth_0'
p472
aS"[('outputspec.mask', 'operand_files')]"
p473
aa(lp474
g355
aS'sca_roi_smooth_0'
p475
aS"[('outputspec.mask', 'operand_files')]"
p476
aa(lp477
g355
aS'sca_seed_smooth_0'
p478
aS"[('outputspec.mask', 'operand_files')]"
p479
aa(lp480
g355
aS'std_dev_1'
p481
aS"[('outputspec.preprocessed', 'func_'), ('outputspec.mask', 'mask_')]"
p482
aa(lp483
g355
ag401
aS"[('outputspec.mask', 'inputspec.subject_mask')]"
p484
aa(lp485
g355
ag176
aS"[('outputspec.mask', 'inputspec.rest_mask'), ('outputspec.example_func', 'inputspec.mean_functional')]"
p486
aa(lp487
g141
ag144
aS"[('outputspec.func_to_anat_linear_xfm_nobbreg', 'inputspec.linear_reg_matrix')]"
p488
aa(lp489
g144
ag7
aS"[('outputspec.func_to_anat_linear_xfm', 'inputspec.affine_file')]"
p490
aa(lp491
g144
ag118
aS"[('outputspec.func_to_anat_linear_xfm', 'inputspec.affine_file')]"
p492
aa(lp493
g144
ag121
aS"[('outputspec.func_to_anat_linear_xfm', 'inputspec.affine_file')]"
p494
aa(lp495
g144
ag124
aS"[('outputspec.func_to_anat_linear_xfm', 'inputspec.affine_file')]"
p496
aa(lp497
g144
ag127
aS"[('outputspec.func_to_anat_linear_xfm', 'inputspec.affine_file')]"
p498
aa(lp499
g144
ag15
aS"[('outputspec.func_to_anat_linear_xfm', 'inputspec.affine_file')]"
p500
aa(lp501
g144
ag132
aS"[('outputspec.func_to_anat_linear_xfm', 'inputspec.affine_file')]"
p502
aa(lp503
g144
ag135
aS"[('outputspec.func_to_anat_linear_xfm', 'inputspec.affine_file')]"
p504
aa(lp505
g144
ag138
aS"[('outputspec.func_to_anat_linear_xfm', 'inputspec.affine_file')]"
p506
aa(lp507
g144
ag57
aS"[('outputspec.anat_func', 'inputspec.underlay')]"
p508
aa(lp509
g144
ag97
aS"[('outputspec.func_to_anat_linear_xfm', 'inputspec.func_to_anat_linear_xfm')]"
p510
aa(lp511
g144
ag159
aS"[('outputspec.func_to_anat_linear_xfm', 'inputspec.affine_file')]"
p512
aa(lp513
g144
ag162
aS"[('outputspec.func_to_anat_linear_xfm', 'inputspec.affine_file')]"
p514
aa(lp515
g144
ag165
aS"[('outputspec.func_to_anat_linear_xfm', 'inputspec.affine_file')]"
p516
aa(lp517
g144
aS'snr_1'
p518
aS"[('outputspec.anat_func', 'mean_func_anat')]"
p519
aa(lp520
g144
ag173
aS"[('outputspec.func_to_anat_linear_xfm', 'xfm_')]"
p521
aa(lp522
g144
ag176
aS"[('outputspec.func_to_anat_linear_xfm', 'inputspec.example_func2highres_mat')]"
p523
aa(lp524
S'fwhm_input'
p525
ag10
aS'[((\'fwhm\', \'S\\\'def set_gauss(fwhm):\\\\n\\\\n    fwhm = float(fwhm)\\\\n\\\\n    sigma = float(fwhm / 2.3548)\\\\n\\\\n    op = "-kernel gauss %f -fmean -mas " % (sigma) + "%s"\\\\n    op_string = op\\\\n\\\\n    return op_string\\\\n\\\'\\n.\', ()), \'op_string\')]'
p526
aa(lp527
g525
ag35
aS'[((\'fwhm\', \'S\\\'def set_gauss(fwhm):\\\\n\\\\n    fwhm = float(fwhm)\\\\n\\\\n    sigma = float(fwhm / 2.3548)\\\\n\\\\n    op = "-kernel gauss %f -fmean -mas " % (sigma) + "%s"\\\\n    op_string = op\\\\n\\\\n    return op_string\\\\n\\\'\\n.\', ()), \'op_string\')]'
p528
aa(lp529
g525
ag182
aS'[((\'fwhm\', \'S\\\'def set_gauss(fwhm):\\\\n\\\\n    fwhm = float(fwhm)\\\\n\\\\n    sigma = float(fwhm / 2.3548)\\\\n\\\\n    op = "-kernel gauss %f -fmean -mas " % (sigma) + "%s"\\\\n    op_string = op\\\\n\\\\n    return op_string\\\\n\\\'\\n.\', ()), \'op_string\')]'
p530
aa(lp531
g525
ag185
aS'[((\'fwhm\', \'S\\\'def set_gauss(fwhm):\\\\n\\\\n    fwhm = float(fwhm)\\\\n\\\\n    sigma = float(fwhm / 2.3548)\\\\n\\\\n    op = "-kernel gauss %f -fmean -mas " % (sigma) + "%s"\\\\n    op_string = op\\\\n\\\\n    return op_string\\\\n\\\'\\n.\', ()), \'op_string\')]'
p532
aa(lp533
g525
ag188
aS'[((\'fwhm\', \'S\\\'def set_gauss(fwhm):\\\\n\\\\n    fwhm = float(fwhm)\\\\n\\\\n    sigma = float(fwhm / 2.3548)\\\\n\\\\n    op = "-kernel gauss %f -fmean -mas " % (sigma) + "%s"\\\\n    op_string = op\\\\n\\\\n    return op_string\\\\n\\\'\\n.\', ()), \'op_string\')]'
p534
aa(lp535
g525
ag191
aS'[((\'fwhm\', \'S\\\'def set_gauss(fwhm):\\\\n\\\\n    fwhm = float(fwhm)\\\\n\\\\n    sigma = float(fwhm / 2.3548)\\\\n\\\\n    op = "-kernel gauss %f -fmean -mas " % (sigma) + "%s"\\\\n    op_string = op\\\\n\\\\n    return op_string\\\\n\\\'\\n.\', ()), \'op_string\')]'
p536
aa(lp537
g525
ag18
aS'[((\'fwhm\', \'S\\\'def set_gauss(fwhm):\\\\n\\\\n    fwhm = float(fwhm)\\\\n\\\\n    sigma = float(fwhm / 2.3548)\\\\n\\\\n    op = "-kernel gauss %f -fmean -mas " % (sigma) + "%s"\\\\n    op_string = op\\\\n\\\\n    return op_string\\\\n\\\'\\n.\', ()), \'op_string\')]'
p538
aa(lp539
g525
ag194
aS'[((\'fwhm\', \'S\\\'def set_gauss(fwhm):\\\\n\\\\n    fwhm = float(fwhm)\\\\n\\\\n    sigma = float(fwhm / 2.3548)\\\\n\\\\n    op = "-kernel gauss %f -fmean -mas " % (sigma) + "%s"\\\\n    op_string = op\\\\n\\\\n    return op_string\\\\n\\\'\\n.\', ()), \'op_string\')]'
p540
aa(lp541
g525
ag472
aS'[((\'fwhm\', \'S\\\'def set_gauss(fwhm):\\\\n\\\\n    fwhm = float(fwhm)\\\\n\\\\n    sigma = float(fwhm / 2.3548)\\\\n\\\\n    op = "-kernel gauss %f -fmean -mas " % (sigma) + "%s"\\\\n    op_string = op\\\\n\\\\n    return op_string\\\\n\\\'\\n.\', ()), \'op_string\')]'
p542
aa(lp543
g525
ag200
aS'[((\'fwhm\', \'S\\\'def set_gauss(fwhm):\\\\n\\\\n    fwhm = float(fwhm)\\\\n\\\\n    sigma = float(fwhm / 2.3548)\\\\n\\\\n    op = "-kernel gauss %f -fmean -mas " % (sigma) + "%s"\\\\n    op_string = op\\\\n\\\\n    return op_string\\\\n\\\'\\n.\', ()), \'op_string\')]'
p544
aa(lp545
g525
ag475
aS'[((\'fwhm\', \'S\\\'def set_gauss(fwhm):\\\\n\\\\n    fwhm = float(fwhm)\\\\n\\\\n    sigma = float(fwhm / 2.3548)\\\\n\\\\n    op = "-kernel gauss %f -fmean -mas " % (sigma) + "%s"\\\\n    op_string = op\\\\n\\\\n    return op_string\\\\n\\\'\\n.\', ()), \'op_string\')]'
p546
aa(lp547
g525
ag203
aS'[((\'fwhm\', \'S\\\'def set_gauss(fwhm):\\\\n\\\\n    fwhm = float(fwhm)\\\\n\\\\n    sigma = float(fwhm / 2.3548)\\\\n\\\\n    op = "-kernel gauss %f -fmean -mas " % (sigma) + "%s"\\\\n    op_string = op\\\\n\\\\n    return op_string\\\\n\\\'\\n.\', ()), \'op_string\')]'
p548
aa(lp549
g525
ag478
aS'[((\'fwhm\', \'S\\\'def set_gauss(fwhm):\\\\n\\\\n    fwhm = float(fwhm)\\\\n\\\\n    sigma = float(fwhm / 2.3548)\\\\n\\\\n    op = "-kernel gauss %f -fmean -mas " % (sigma) + "%s"\\\\n    op_string = op\\\\n\\\\n    return op_string\\\\n\\\'\\n.\', ()), \'op_string\')]'
p550
aa(lp551
g525
ag206
aS'[((\'fwhm\', \'S\\\'def set_gauss(fwhm):\\\\n\\\\n    fwhm = float(fwhm)\\\\n\\\\n    sigma = float(fwhm / 2.3548)\\\\n\\\\n    op = "-kernel gauss %f -fmean -mas " % (sigma) + "%s"\\\\n    op_string = op\\\\n\\\\n    return op_string\\\\n\\\'\\n.\', ()), \'op_string\')]'
p552
aa(lp553
g525
ag209
aS'[((\'fwhm\', \'S\\\'def set_gauss(fwhm):\\\\n\\\\n    fwhm = float(fwhm)\\\\n\\\\n    sigma = float(fwhm / 2.3548)\\\\n\\\\n    op = "-kernel gauss %f -fmean -mas " % (sigma) + "%s"\\\\n    op_string = op\\\\n\\\\n    return op_string\\\\n\\\'\\n.\', ()), \'op_string\')]'
p554
aa(lp555
g525
ag212
aS'[((\'fwhm\', \'S\\\'def set_gauss(fwhm):\\\\n\\\\n    fwhm = float(fwhm)\\\\n\\\\n    sigma = float(fwhm / 2.3548)\\\\n\\\\n    op = "-kernel gauss %f -fmean -mas " % (sigma) + "%s"\\\\n    op_string = op\\\\n\\\\n    return op_string\\\\n\\\'\\n.\', ()), \'op_string\')]'
p556
aa(lp557
g525
ag215
aS'[((\'fwhm\', \'S\\\'def set_gauss(fwhm):\\\\n\\\\n    fwhm = float(fwhm)\\\\n\\\\n    sigma = float(fwhm / 2.3548)\\\\n\\\\n    op = "-kernel gauss %f -fmean -mas " % (sigma) + "%s"\\\\n    op_string = op\\\\n\\\\n    return op_string\\\\n\\\'\\n.\', ()), \'op_string\')]'
p558
aa(lp559
g525
ag218
aS'[((\'fwhm\', \'S\\\'def set_gauss(fwhm):\\\\n\\\\n    fwhm = float(fwhm)\\\\n\\\\n    sigma = float(fwhm / 2.3548)\\\\n\\\\n    op = "-kernel gauss %f -fmean -mas " % (sigma) + "%s"\\\\n    op_string = op\\\\n\\\\n    return op_string\\\\n\\\'\\n.\', ()), \'op_string\')]'
p560
aa(lp561
g407
aS'fd_plot_1'
p562
aS"[('outputspec.FD_1D', 'arr'), ('outputspec.frames_ex_1D', 'ex_vol')]"
p563
aa(lp564
g407
aS'log_gen_motion_stats_0'
p565
aS"[('outputspec.motion_params', 'inputspec.inputs')]"
p566
aa(lp567
S'mask_dataflow_0'
p568
ag239
aS"[('outputspec.out_file', 'reference')]"
p569
aa(lp570
g568
aS'voxel_timeseries_0'
p571
aS"[('outputspec.out_file', 'input_mask.mask')]"
p572
aa(lp573
S'mask_dataflow_for_sca_0'
p574
ag242
aS"[('outputspec.out_file', 'reference')]"
p575
aa(lp576
g574
aS'voxel_timeseries_for_sca_0'
p577
aS"[('outputspec.out_file', 'input_mask.mask')]"
p578
aa(lp579
g97
ag6
aS"[('outputspec.subject', 'inputspec.rest_res')]"
p580
aa(lp581
g97
ag386
aS"[('outputspec.subject', 'realigned_file')]"
p582
aa(lp583
g97
aS'log_nuisance_0'
p584
aS"[('outputspec.subject', 'inputspec.inputs')]"
p585
aa(lp586
g392
aS'log_reho_0'
p587
aS"[('outputspec.raw_reho_map', 'inputspec.inputs')]"
p588
aa(lp589
g392
ag159
aS"[('outputspec.raw_reho_map', 'inputspec.source_file')]"
p590
aa(lp591
g392
ag472
aS"[('outputspec.raw_reho_map', 'in_file')]"
p592
aa(lp593
g392
aS'reho_to_standard_0'
p594
aS"[('outputspec.raw_reho_map', 'inputspec.input_image')]"
p595
aa(lp596
g100
ag594
aS"[('outputspec.transformation_series', 'inputspec.transforms')]"
p597
aa(lp598
g159
ag100
aS"[('outputspec.itk_transform', 'inputspec.fsl_to_itk_affine')]"
p599
aa(lp600
g472
aS'reho_smooth_mean_0'
p601
aS"[('out_file', 'in_file')]"
p602
aa(lp603
g601
aS'reho_smooth_mean_to_txt_0'
p604
aS"[('out_file', 'in_file')]"
p605
aa(lp606
g594
ag200
aS"[('outputspec.output_image', 'in_file')]"
p607
aa(lp608
g200
ag295
aS"[('out_file', 'measure_file')]"
p609
aa(lp610
g200
aS'hist_reho_1'
p611
aS"[('out_file', 'measure_file')]"
p612
aa(lp613
g200
aS'log_reho_to_standard_smooth_0'
p614
aS"[('out_file', 'inputspec.inputs')]"
p615
aa(lp616
g200
aS'reho_to_standard_smooth_mean_0'
p617
aS"[('out_file', 'in_file')]"
p618
aa(lp619
g200
ag232
aS"[('out_file', 'inputspec.input_file')]"
p620
aa(lp621
g617
aS'reho_to_standard_smooth_mean_to_txt_0'
p622
aS"[('out_file', 'in_file')]"
p623
aa(lp624
g239
ag571
aS"[('out_file', 'inputspec.rest')]"
p625
aa(lp626
g242
ag577
aS"[('out_file', 'inputspec.rest')]"
p627
aa(lp628
g245
aS'roi_timeseries_0'
p629
aS"[('out_file', 'inputspec.rest')]"
p630
aa(lp631
g248
aS'roi_timeseries_for_sca_0'
p632
aS"[('out_file', 'inputspec.rest')]"
p633
aa(lp634
g251
ag221
aS"[('out_file', 'inputspec.spatial_map')]"
p635
aa(lp636
S'roi_dataflow_0'
p637
ag245
aS"[('outputspec.out_file', 'reference')]"
p638
aa(lp639
g637
ag629
aS"[('outputspec.out_file', 'input_roi.roi')]"
p640
aa(lp641
S'roi_dataflow_for_sca_0'
p642
ag248
aS"[('outputspec.out_file', 'reference')]"
p643
aa(lp644
g642
ag632
aS"[('outputspec.out_file', 'input_roi.roi')]"
p645
aa(lp646
g629
aS'log_roi_timeseries_0'
p647
aS"[('outputspec.roi_outputs', 'inputspec.inputs')]"
p648
aa(lp649
g632
aS'fisher_z_score_std_sca_roi_0'
p650
aS"[('outputspec.roi_outputs', 'inputspec.timeseries_one_d')]"
p651
aa(lp652
g632
aS'log_roi_timeseries_for_sca_0'
p653
aS"[('outputspec.roi_outputs', 'inputspec.inputs')]"
p654
aa(lp655
g632
ag395
aS'[((\'outputspec.roi_outputs\', \'S\\\'def extract_one_d(list_timeseries):\\\\n    for timeseries in list_timeseries:\\\\n        if \\\\\\\'1D\\\\\\\' in timeseries:\\\\n            return timeseries\\\\n        else:\\\\n            print "Error : ROI/Voxel TimeSeries 1D file not found"\\\\n            return None\\\\n\\\'\\n.\', ()), \'inputspec.timeseries_one_d\')]'
p656
aa(lp657
g632
ag224
aS'[((\'outputspec.roi_outputs\', \'S\\\'def extract_txt(list_timeseries):\\\\n    """\\\\n    Method to extract txt file containing \\\\n    roi timeseries required for dual regression\\\\n    """\\\\n\\\\n    out_file = None\\\\n    for timeseries in list_timeseries:\\\\n        if timeseries.endswith(\\\\\\\'.txt\\\\\\\'):\\\\n            out_file = timeseries\\\\n\\\\n    if not out_file:\\\\n        raise Exception("Unable to retrieve roi timeseries txt"\\\\\\\\\\\\n                          " file required for dual regression")\\\\n\\\\n    return out_file\\\\n\\\'\\n.\', ()), \'inputspec.subject_timeseries\')]'
p658
aa(lp659
g395
aS'log_sca_roi_0'
p660
aS"[('outputspec.correlation_file', 'inputspec.inputs')]"
p661
aa(lp662
g395
ag162
aS"[('outputspec.correlation_file', 'inputspec.source_file')]"
p663
aa(lp664
g395
ag475
aS"[('outputspec.correlation_file', 'in_file')]"
p665
aa(lp666
g395
aS'sca_roi_to_standard_0'
p667
aS"[('outputspec.correlation_file', 'inputspec.input_image')]"
p668
aa(lp669
g103
ag667
aS"[('outputspec.transformation_series', 'inputspec.transforms')]"
p670
aa(lp671
g162
ag103
aS"[('outputspec.itk_transform', 'inputspec.fsl_to_itk_affine')]"
p672
aa(lp673
g475
aS'sca_roi_smooth_mean_0'
p674
aS"[('out_file', 'in_file')]"
p675
aa(lp676
g674
aS'sca_roi_smooth_mean_to_txt_0'
p677
aS"[('out_file', 'in_file')]"
p678
aa(lp679
g667
ag203
aS"[('outputspec.output_image', 'in_file')]"
p680
aa(lp681
g203
ag650
aS"[('out_file', 'inputspec.correlation_file')]"
p682
aa(lp683
g203
aS'log_sca_roi_to_standard_smooth_0'
p684
aS"[('out_file', 'inputspec.inputs')]"
p685
aa(lp686
g203
aS'sca_roi_to_standard_smooth_mean_0'
p687
aS"[('out_file', 'in_file')]"
p688
aa(lp689
g687
aS'sca_roi_to_standard_smooth_mean_to_txt_0'
p690
aS"[('out_file', 'in_file')]"
p691
aa(lp692
g398
ag165
aS"[('outputspec.correlation_file', 'inputspec.source_file')]"
p693
aa(lp694
g398
ag478
aS"[('outputspec.correlation_file', 'in_file')]"
p695
aa(lp696
g398
aS'sca_seed_to_standard_0'
p697
aS"[('outputspec.correlation_file', 'inputspec.input_image')]"
p698
aa(lp699
g106
ag697
aS"[('outputspec.transformation_series', 'inputspec.transforms')]"
p700
aa(lp701
g165
ag106
aS"[('outputspec.itk_transform', 'inputspec.fsl_to_itk_affine')]"
p702
aa(lp703
g478
aS'sca_seed_smooth_mean_0'
p704
aS"[('out_file', 'in_file')]"
p705
aa(lp706
g704
aS'sca_seed_smooth_mean_to_txt_0'
p707
aS"[('out_file', 'in_file')]"
p708
aa(lp709
g697
ag206
aS"[('outputspec.output_image', 'in_file')]"
p710
aa(lp711
g206
aS'fisher_z_score_std_sca_seed_0'
p712
aS"[('out_file', 'inputspec.correlation_file')]"
p713
aa(lp714
g206
aS'log_sca_seed_to_standard_smooth_0'
p715
aS"[('out_file', 'inputspec.inputs')]"
p716
aa(lp717
g206
aS'sca_seed_to_standard_smooth_mean_0'
p718
aS"[('out_file', 'in_file')]"
p719
aa(lp720
g718
aS'sca_seed_to_standard_smooth_mean_to_txt_0'
p721
aS"[('out_file', 'in_file')]"
p722
aa(lp723
g209
ag310
aS"[('out_file', 'measure_file')]"
p724
aa(lp725
g209
aS'hist_dr_sca_1'
p726
aS"[('out_file', 'measure_file')]"
p727
aa(lp728
g218
aS'log_sca_tempreg_maps_stack_smooth_0'
p729
aS"[('out_file', 'inputspec.inputs')]"
p730
aa(lp731
g438
aS'convert_tr_0'
p732
aS"[('tr', 'tr')]"
p733
aa(lp734
g438
ag354
aS"[('start_indx', 'inputspec.start_idx'), ('stop_indx', 'inputspec.stop_idx')]"
p735
aa(lp736
g109
ag144
aS'[((\'outputspec.probability_maps\', "S\'def pick_wm(seg_prob_list):\\\\n    seg_prob_list.sort()\\\\n    return seg_prob_list[-1]\\\\n\'\\n.", ()), \'inputspec.anat_wm_segmentation\')]'
p737
aa(lp738
g109
aS'log_seg_preproc_0'
p739
aS"[('outputspec.partial_volume_map', 'inputspec.inputs')]"
p740
aa(lp741
g109
ag150
aS"[('outputspec.csf_mask', 'inputspec.overlay_csf'), ('outputspec.wm_mask', 'inputspec.overlay_wm'), ('outputspec.gm_mask', 'inputspec.overlay_gm')]"
p742
aa(lp743
g109
ag97
aS"[('outputspec.gm_mask', 'inputspec.gm_mask'), ('outputspec.wm_mask', 'inputspec.wm_mask'), ('outputspec.csf_mask', 'inputspec.csf_mask')]"
p744
aa(lp745
g170
ag153
aS"[('new_fname', 'inputspec.overlay')]"
p746
aa(lp747
g518
ag303
aS"[('new_fname', 'measure_file')]"
p748
aa(lp749
g518
aS'hist_snr_1'
p750
aS"[('new_fname', 'measure_file')]"
p751
aa(lp752
g518
aS'snr_val1'
p753
aS"[('new_fname', 'measure_file')]"
p754
aa(lp755
S'spatial_map_dataflow_0'
p756
ag251
aS"[('select_spatial_map.out_file', 'in_file')]"
p757
aa(lp758
g221
aS'log_spatial_map_timeseries_0'
p759
aS"[('outputspec.subject_timeseries', 'inputspec.inputs')]"
p760
aa(lp761
g221
ag401
aS"[('outputspec.subject_timeseries', 'inputspec.subject_timeseries')]"
p762
aa(lp763
g481
ag173
aS"[('new_fname', 'func_')]"
p764
aa(lp765
g173
ag518
aS"[('new_fname', 'std_dev')]"
p766
aa(lp767
g401
ag118
aS"[('outputspec.temp_reg_map_files', 'inputspec.source_file')]"
p768
aa(lp769
g401
ag323
aS"[('outputspec.temp_reg_map_files', 'inputspec.input_image')]"
p770
aa(lp771
g401
ag121
aS"[('outputspec.temp_reg_map', 'inputspec.source_file')]"
p772
aa(lp773
g401
ag330
aS"[('outputspec.temp_reg_map', 'inputspec.input_image')]"
p774
aa(lp775
g401
ag124
aS"[('outputspec.temp_reg_map_z_files', 'inputspec.source_file')]"
p776
aa(lp777
g401
ag340
aS"[('outputspec.temp_reg_map_z_files', 'inputspec.input_image')]"
p778
aa(lp779
g401
ag127
aS"[('outputspec.temp_reg_map_z', 'inputspec.source_file')]"
p780
aa(lp781
g401
ag347
aS"[('outputspec.temp_reg_map_z', 'inputspec.input_image')]"
p782
aa(lp783
g401
aS'log_temporal_dual_regression_0'
p784
aS"[('outputspec.temp_reg_map', 'inputspec.inputs')]"
p785
aa(lp786
g224
aS'log_temporal_regression_sca_0'
p787
aS"[('outputspec.temp_reg_map', 'inputspec.inputs')]"
p788
aa(lp789
g224
ag209
aS"[('outputspec.temp_reg_map_z_files', 'in_file')]"
p790
aa(lp791
g224
ag212
aS"[('outputspec.temp_reg_map_z', 'in_file')]"
p792
aa(lp793
g224
ag215
aS"[('outputspec.temp_reg_map_files', 'in_file')]"
p794
aa(lp795
g224
ag218
aS"[('outputspec.temp_reg_map', 'in_file')]"
p796
aa(lp797
g176
ag314
aS"[('outputspec.VMHC_Z_stat_FWHM_img', 'measure_file')]"
p798
aa(lp799
g176
aS'hist_vmhc_1'
p800
aS"[('outputspec.VMHC_Z_stat_FWHM_img', 'measure_file')]"
p801
aa(lp802
g176
aS'log_vmhc_0'
p803
aS"[('outputspec.VMHC_FWHM_img', 'inputspec.inputs')]"
p804
aa(lp805
g571
aS'log_voxel_timeseries_0'
p806
aS"[('outputspec.mask_outputs', 'inputspec.inputs')]"
p807
aa(lp808
g577
ag712
aS"[('outputspec.mask_outputs', 'inputspec.timeseries_one_d')]"
p809
aa(lp810
g577
aS'log_voxel_timeseries_for_sca_0'
p811
aS"[('outputspec.mask_outputs', 'inputspec.inputs')]"
p812
aa(lp813
g577
ag398
aS'[((\'outputspec.mask_outputs\', \'S\\\'def extract_one_d(list_timeseries):\\\\n    for timeseries in list_timeseries:\\\\n        if \\\\\\\'1D\\\\\\\' in timeseries:\\\\n            return timeseries\\\\n        else:\\\\n            print "Error : ROI/Voxel TimeSeries 1D file not found"\\\\n            return None\\\\n\\\'\\n.\', ()), \'inputspec.timeseries_one_d\')]'
p814
aa(lp815
g50
ag283
aS"[('outputspec.z_score_img', 'measure_file')]"
p816
aa(lp817
g50
aS'hist_alff_zstd_1'
p818
aS"[('outputspec.z_score_img', 'measure_file')]"
p819
aa(lp820
g229
ag291
aS"[('outputspec.z_score_img', 'measure_file')]"
p821
aa(lp822
g229
aS'hist_falff_zstd_1'
p823
aS"[('outputspec.z_score_img', 'measure_file')]"
p824
aa(lp825
g232
ag299
aS"[('outputspec.z_score_img', 'measure_file')]"
p826
aa(lp827
g232
aS'hist_reho_zstd_1'
p828
aS"[('outputspec.z_score_img', 'measure_file')]"
p829
aa.