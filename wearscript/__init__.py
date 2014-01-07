from socket import websocket_client_factory,websocket_server 

def parse(callback, parser):
    subparsers = parser.add_subparsers()
    subparser = subparsers.add_parser('server')
    subparser.add_argument('websocket_port', type=int)
    subparser.set_defaults(func_=websocket_server)
    subparser = subparsers.add_parser('client')
    subparser.add_argument('client_endpoint')
    subparser.set_defaults(func_=websocket_client_factory)
    args = parser.parse_args()
    vargs = dict(vars(args))
    del vargs['func_']
    args.func_(callback, **vargs)
