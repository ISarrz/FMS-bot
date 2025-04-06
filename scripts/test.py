class Class:
    def __del__(self):
        print('del')


cls = Class()

del cls

pass