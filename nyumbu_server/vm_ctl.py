import argparse
import os
from .src.nyumbu_server.vm import VM

def start(file):
    print(f"Starting {file} ...")
    # 此处放置启动"file"的代码

def stop(file):
    print(f"Stopping {file} ...")
    # 此处放置停止"file"的代码

def main():

    parser = argparse.ArgumentParser(prog = 'vm_ctl')

    subparsers = parser.add_subparsers(dest='command')

    # 一级命令 ('start' or 'stop')
    command_parser = subparsers.add_parser('start')
    command_parser.add_argument('file', help='the file to start')
    command_parser = subparsers.add_parser('stop')
    command_parser.add_argument('file', help='the file to stop')

    # 二级命令 ('consrol start' or 'consrol stop')
    command_parser = subparsers.add_parser('consrol')
    consrol_subparser = command_parser.add_subparsers(dest='consrol_command')
    command_parser = consrol_subparser.add_parser('start')
    command_parser.add_argument('file', help='the file to start under consrol command')
    command_parser = consrol_subparser.add_parser('stop')
    command_parser.add_argument('file', help='the file to stop under consrol command')

    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"The file {args.file} does not exist.")
        exit(1)

    if args.command == 'start' or (args.command == 'consrol' and args.consrol_command == 'start'):
        vm = VM(open(args.file).read())
        vm.start()
    elif args.command == 'stop' or (args.command == 'consrol' and args.consrol_command == 'stop'):
        vm = VM(open(args.file).read())
        vm.stop()

if __name__ == "__main__":
    main()