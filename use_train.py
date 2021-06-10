from own_trainer import trainer
import argparse


# output root
# output name
# LR
# 



def main(input_root, lr, output_folder):

	print(input_root + ".hdf5")
	trainer(input_hdf5=input_root + ".hdf5",
		input_csv=input_root + '.csv',
		output_name='{}_LR1e-{}'.format(output_folder, lr),      
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
		__lr = 10**(-lr)
		)

parser = argparse.ArgumentParser()
parser.add_argument('input_root', type = str, help = "file root to .hdf5 and .csv pair")
parser.add_argument('lr', type = int, help = "learning rate exponent")
parser.add_argument('output_folder', type = str, help = "name of the folder in the same directory to save the model to")

args = parser.parse_args()


main(args.input_root, args.lr, args.output_folder)
