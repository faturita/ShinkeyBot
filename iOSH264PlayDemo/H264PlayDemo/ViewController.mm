//
//  ViewController.m
//  H264PlayDemo
//
//  Created by 王爽 on 16/6/27.
//  Copyright © 2016年 王爽. All rights reserved.
//

#import <SystemConfiguration/CaptiveNetwork.h>
#import "ViewController.h"
#import "VideoFileParser.h"
#import "VideoNetworkParser.h"
#import "FFMPEGH264Decoder.h"
#import "OpenGLView20.h"
#import "GCDAsyncUdpSocket.h"
#import "GCDAsyncSocket.h"

#import <mach/mach_time.h>

// These are the default address where ShinkeyBot listens.
#define SHINKEYBOTADDRESS   @"10.17.10.107"

// Multicast port and group IP
#define MYPORT      8123
#define MYGROUP_4   @"225.0.0.250"

#define COMMAND_UDP_PORT    10001

@interface ViewController ()
@property (weak, nonatomic) IBOutlet UIButton *connectionButton;

@end

@implementation ViewController

// UDP Socket for Commands
GCDAsyncUdpSocket *_udpSocket ;

// Multicast UDP Socket for Initial connection.
GCDAsyncUdpSocket *_mudpSocket;

OpenGLView20 *_glView;

bool _connect;

- (void)viewDidLoad {
    [super viewDidLoad];
    
    _shinkeybotaddress = SHINKEYBOTADDRESS;
    [self recoverStoredAddress];
    
    //    [_commandText setDelegate:self];
    
    [self setupSocket];
    
    _udpSocket = [[GCDAsyncUdpSocket alloc] initWithDelegate:self delegateQueue:dispatch_get_main_queue()];
    
    
    CGFloat screenWidth = [UIScreen mainScreen].bounds.size.width;
    CGFloat ratio = 480.0 / 640.0;
    OpenGLView20 *glView = [[OpenGLView20 alloc] initWithFrame:CGRectMake(0, 40, screenWidth, screenWidth *ratio)];
    glView.backgroundColor = [UIColor blackColor];
    [self.view addSubview:glView];
    
    _glView = glView;
    _connect = false;
    
    NSString *filePath = [[NSBundle mainBundle] pathForResource:@"demo.h264" ofType:nil];
    NSLog(@"%@",filePath);
    
}

- (void)setupSocket
{
    _mudpSocket = [[GCDAsyncUdpSocket alloc] initWithDelegate:self delegateQueue:dispatch_get_main_queue()];
    NSError *error = nil;
    if (![_mudpSocket bindToPort:MYPORT error:&error])
    {
        NSLog(@"Error binding to port: %@", error);
        return;
    }
    //225.0.0.250
    //226.1.1.1
    if(![_mudpSocket joinMulticastGroup:MYGROUP_4 error:&error]){
        NSLog(@"Error connecting to multicast group: %@", error);
        return;
    }
    if (![_mudpSocket beginReceiving:&error])
    {
        NSLog(@"Error receiving: %@", error);
        return;
    }
    NSLog(@"Listening on Multicast UDP interface for incoming connections.");
}

// Store the IP Address that we obtained in user preferences.
- (void)storeAddress:(NSString*)address {
    // To save data
    NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
    [defaults setObject:address forKey:@"shinkeybotaddress"];
    
    [defaults synchronize];
    NSLog(@"Host IP Address saved to defaults.");
}

- (void)recoverStoredAddress {
    // To retrive it back
    NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
    NSString *address = [defaults objectForKey:@"shinkeybotaddress"];
    //int srno = [defaults integerForKey:@"kSrNo"];
    if (address != nil)
    {
        _shinkeybotaddress = address;
        NSLog(@"Data from defaults--> Address: %@",address);
    }
}

// UDP Command Messages
+ (void)send:(NSString*)host withMessage:(NSString*)message
{
    [self send:host withPort:COMMAND_UDP_PORT withMessage:message];
}

+ (void)send:(NSString*)host withPort:(int)port withMessage:(NSString *)message
{
    NSData* data = [[NSString stringWithString:message] dataUsingEncoding:NSASCIIStringEncoding];
    
    NSLog(@"Send message %@ to %@", message, host);
    
    [_udpSocket sendData:data toHost:host port:port withTimeout:-1 tag:1];
}

+ (NSString *)currentWifiSSID {
    // Does not work on the simulator.
    NSString *ssid = nil;
    NSArray *ifs = (__bridge_transfer id)CNCopySupportedInterfaces();
    for (NSString *ifnam in ifs) {
        NSDictionary *info = (__bridge_transfer id)CNCopyCurrentNetworkInfo((__bridge CFStringRef)ifnam);
        if (info[@"SSID"]) {
            ssid = info[@"SSID"];
        }
    }
    return ssid;
}


- (void)udpSocket:(GCDAsyncUdpSocket *)sock didReceiveData:(NSData *)data fromAddress:   (NSData *)address withFilterContext:(id)filterContext
{
    NSString *msg = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
    
    NSString *host = nil;
    uint16_t port = 0;
    
    [GCDAsyncUdpSocket getHost:&host port:&port fromAddress:address];
    
    if (msg)
    {
        NSLog(@"Message = %@, Adress = %@ %i",msg,host,port);
        _shinkeybotaddress = host;
        [self storeAddress:host];
    }
    else
    {
        NSLog(@"Error converting received data into UTF-8 String");
    }
}

- (void)viewDidDisappear:(BOOL)animated
{
    [super viewDidDisappear:animated];
    
    [_udpSocket close];
    
    _udpSocket = NULL;
}


- (IBAction)doStop:(id)sender {
    [ViewController send:_shinkeybotaddress withMessage:[NSString stringWithFormat:@"U 000"]];
}

- (IBAction)doUp:(id)sender {
    [ViewController send:_shinkeybotaddress withMessage:[NSString stringWithFormat:@"UW000"]];
}
- (IBAction)doDown:(id)sender {
    [ViewController send:_shinkeybotaddress withMessage:[NSString stringWithFormat:@"US000"]];
}

- (IBAction)doRight:(id)sender {
    [ViewController send:_shinkeybotaddress withMessage:[NSString stringWithFormat:@"UD000"]];
}
- (IBAction)changeSpeed:(id)sender {
    UISwitch *mySwitch = (UISwitch *)sender;
    if ([mySwitch isOn]) {
        [ViewController send:_shinkeybotaddress withMessage:[NSString stringWithFormat:@"U,000"]];
    } else {
        [ViewController send:_shinkeybotaddress withMessage:[NSString stringWithFormat:@"U.000"]];
    }
}
- (IBAction)doLeft:(id)sender {
    [ViewController send:_shinkeybotaddress withMessage:[NSString stringWithFormat:@"UA000"]];
}

- (IBAction)doConnect:(id)sender {
    
    if (_connect)
    {
        _connect = false;
        [_connectionButton setImage:[UIImage imageNamed:@"connect"] forState:UIControlStateNormal];
    }
    else {
    
        VideoNetworkParser *parser = [VideoNetworkParser alloc];
        [parser open:_shinkeybotaddress];
        
        CFFMPEGH264Decoder *decoder = new CFFMPEGH264Decoder(0);
        decoder->Init();
        decoder->Start();
        dispatch_queue_t decodeQueue = dispatch_queue_create("abc", NULL);
        dispatch_async(decodeQueue, ^{
            VideoPacket *vp = nil;
            int toomanyerrors=0;
            while(true) {
                vp = [parser nextPacket];
                if(vp == nil) {
                    //NSLog(@"Error reading next packet.");
                    toomanyerrors++;
                    if (toomanyerrors>1000000) {
                        
                    }
                    
                    if (!_connect)
                    {
                        break;
                    }
                    
                    continue;
                }
                decoder->Decode(vp.buffer, vp.size);
                unsigned char *result = decoder->GetResultData();
                if (result != 0) {
                    //  NSLog(@"%d, %d",decoder->GetResultWidth(), decoder->GetResultHeight());
                    dispatch_async(dispatch_get_main_queue(), ^{
                        [_glView displayYUV420pData:result width:decoder->GetResultWidth() height:decoder->GetResultHeight()];
                    });
                    
                    decoder->ReleaseResultData();
                }
            }
        });
        
        _connect = true;
        [_connectionButton setImage:[UIImage imageNamed:@"connected"] forState:UIControlStateNormal];
    }
}


- (IBAction)handlePan:(UIPanGestureRecognizer*)recognizer {
    [recognizer translationInView:self.view];
        
    
}

@end
