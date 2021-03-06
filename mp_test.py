from multiprocessing import Queue
from multiprocessing import Process
from multiprocessing import Lock, Process, Queue, current_process
import time
import queue # imported for using queue.Empty exception


def test_queue():
	colors = ['red', 'green', 'blue', 'black']
	cnt = 1
	# instantiating a queue object
	queue = Queue()
	print('pushing items to queue:')
	for color in colors:
		print('item no: ', cnt, ' ', color)
		queue.put(color)
		cnt += 1

	print('\npopping items from queue:')
	cnt = 0
	while not queue.empty():
		print('item no: ', cnt, ' ', queue.get())
		cnt += 1
def test_process():
	
	def print_func(continent='Asia'):
		print('The name of continent is : ', continent)

	if __name__ == "__main__":  # confirms that the code is under main function
		names = ['America', 'Europe', 'Africa']
		procs = []
		proc = Process(target=print_func)  # instantiating without any argument
		procs.append(proc)
		proc.start()

		# instantiating process with arguments
		for name in names:
			# print(name)
			proc = Process(target=print_func, args=(name,))
			procs.append(proc)
			proc.start()

		# complete the processes
		for proc in procs:
			proc.join()

def test_lock():
	def do_job(tasks_to_accomplish, tasks_that_are_done):
		while True:
			try:
				'''
					try to get task from the queue. get_nowait() function will 
					raise queue.Empty exception if the queue is empty. 
					queue(False) function would do the same task also.
				'''
				task = tasks_to_accomplish.get_nowait()
			except queue.Empty:

				break
			else:
				'''
					if no exception has been raised, add the task completion 
					message to task_that_are_done queue
				'''
				print(task)
				tasks_that_are_done.put(task + ' is done by ' + current_process().name)
				time.sleep(.5)
		return True


	def main():
		number_of_task = 10
		number_of_processes = 4
		tasks_to_accomplish = Queue()
		tasks_that_are_done = Queue()
		processes = []

		for i in range(number_of_task):
			tasks_to_accomplish.put("Task no " + str(i))

		# creating processes
		for w in range(number_of_processes):
			p = Process(target=do_job, args=(tasks_to_accomplish, tasks_that_are_done))
			processes.append(p)
			p.start()

		# completing process
		for p in processes:
			p.join()

		# print the output
		while not tasks_that_are_done.empty():
			print(tasks_that_are_done.get())

		return True
	main()

#test_lock()
#test_process()
test_queue()
