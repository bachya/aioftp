"""Simple aioftp-based server with one user (anonymous or not)"""
import asyncio
import logging

import argparse

import aioftp


parser = argparse.ArgumentParser(
    prog="aioftp",
    usage="%(prog)s [options]",
    description="Simple aioftp-based server with one user (anonymous or not)."
)
parser.add_argument("--user", metavar="LOGIN", dest="login",
                    help="user name to login")
parser.add_argument("--pass", metavar="PASSWORD", dest="password",
                    help="password to login")
parser.add_argument("-d", metavar="DIRECTORY", dest="home",
                    help="the directory to share (default current directory)")
parser.add_argument("-q", "--quiet", action="store_true",
                    help="set logging level to 'ERROR' instead of 'INFO'")
parser.add_argument("--memory", action="store_true", help="use memory storage")
parser.add_argument("--host", default="0.0.0.0",
                    help="host for binding [default: %(default)s]")
parser.add_argument("--port", type=int, default=2121,
                    help="port for binding [default: %(default)s]")

args = parser.parse_args()
print("aioftp v{}".format(aioftp.__version__))

if not args.quiet:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(message)s",
        datefmt="[%H:%M:%S]:",
    )
if args.memory:
    user = aioftp.User(args.login, args.password, base_path="/")
    path_io_factory = aioftp.MemoryPathIO
else:
    if args.home:
        user = aioftp.User(args.login, args.password, base_path=args.home)
    else:
        user = aioftp.User(args.login, args.password)
    path_io_factory = aioftp.PathIO

server = aioftp.Server([user], path_io_factory=path_io_factory)

loop = asyncio.get_event_loop()
loop.run_until_complete(server.start(args.host, args.port))
try:
    loop.run_forever()
except KeyboardInterrupt:
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
