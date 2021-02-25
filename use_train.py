from own_trainer import trainer

trainer(input_hdf5='/home/zchoong001/cy1400/cy1400-eqt/EQTransformer/ModelsAndSampleData/100samples.hdf5',
    input_csv='/home/zchoong001/cy1400/cy1400-eqt/EQTransformer/ModelsAndSampleData/100samples.csv',
    output_name='models/100samplesmodel',                
    cnn_blocks=5,
    lstm_blocks=2,
    padding='same',
    activation='relu',
    drop_rate=0.2,
    label_type='gaussian',
    add_event_r=0.6,
    add_gap_r=0.2,
    shift_event_r=0.9,
    add_noise_r=0.5, 
    mode='generator',
    loss_weights = [0.03, 0.40, 0.58],
    loss_types = ['binary_crossentropy', 'binary_crossentropy', 'binary_crossentropy'],
    train_valid_test_split=[0.60, 0.20, 0.20],
    batch_size=20,
    epochs=10, 
    patience=2,
    gpuid=None,
    gpu_limit=None)