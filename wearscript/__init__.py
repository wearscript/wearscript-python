from socket import websocket_client_factory,websocket_server 

def parse(callback, parser):

    parser.add_argument('--server',metavar="PORT",type=int)
    parser.add_argument('--client_endpoint')

    args = parser.parse_args()
    vargs = dict(vars(args))

    if args.server:
        websocket_server(callback,args.server,**vargs)
    else:
        websocket_client_factory(callback,**vargs)



