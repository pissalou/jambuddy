import mido

if __name__ == '__main__':
    print(mido.get_output_names())
    print(len(mido.get_output_names()))
    print(mido.get_output_names()[0])
