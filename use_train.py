from own_trainer import trainer

for c,i in enumerate([1e-2, 1e-3, 1e-4, 1e-5]):
	trainer(input_hdf5='/home/zchoong001/cy1400/cy1400-eqt/training_files/STEAD_1000_noise.hdf5',
		input_csv='/home/zchoong001/cy1400/cy1400-eqt/training_files/STEAD_1000_noise.csv',
		output_name='models/1000samples_noiseonly_LR{}'.format(i),      
		# i suspect the output_name cannot have / or it will confuse the saving     
		cnn_blocks=5,
		lstm_blocks=2,
		padding='same',
		activation='relu',
		drop_rate=0.1,
		label_type='gaussian',
		#add_event_r=0.6,
		#add_gap_r=0.2,
		#shift_event_r=0.9,
		#add_noise_r=0.5, 
		mode='generator',
		#loss_weights = [0.03, 0.40, 0.58],
		loss_types = ['binary_crossentropy', 'binary_crossentropy', 'binary_crossentropy'],
		train_valid_test_split=[0.75, 0.05, 0.20],
		batch_size=20,
		epochs=100, 
		patience=10,
		gpuid=None,
		gpu_limit=None,
		_learning_rate=i)