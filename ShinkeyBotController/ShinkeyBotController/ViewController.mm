//
//  ViewController.m
//  ShinkeyBotController
//  https://developer.apple.com/library/content/documentation/Cocoa/Conceptual/BinaryData/Tasks/WorkingMutableData.html#//apple_ref/doc/uid/20002150
//  https://github.com/robbiehanson/CocoaAsyncSocket/wiki/Reference_GCDAsyncSocket
//  Created by Rodrigo Ramele on 10/10/16.
//  Copyright © 2016 Baufest. All rights reserved.
//

#import <SystemConfiguration/CaptiveNetwork.h>
#import <AVFoundation/AVFoundation.h>
#import <AssetsLibrary/ALAsset.h>
#import <AssetsLibrary/ALAssetRepresentation.h>
#import <ImageIO/CGImageSource.h>
#import <ImageIO/CGImageProperties.h>
#import "ViewController.h"
#import "GCDAsyncUdpSocket.h"
#import "GCDAsyncSocket.h"
#import <opencv2/opencv.hpp>

#import <mach/mach_time.h>

// These are the default address where ShinkeyBot listens.
#define SHINKEYBOTADDRESS   @"10.17.10.22"
#define dshinkeybotaddress   @"10.17.13.89"

// Multicast port and group IP
#define MYPORT      8123
#define MYGROUP_4   @"225.0.0.250"


#define COMMAND_UDP_PORT    10001


@interface ViewController ()
@property (weak, nonatomic) IBOutlet UIImageView *imageView;
@property (weak, nonatomic) IBOutlet UITextField *commandText;
@property (weak, nonatomic) IBOutlet UISwitch *aheadswitch;
@end

@implementation ViewController
AVCaptureVideoPreviewLayer *_previewLayer;
AVCaptureSession *_captureSession;
AVCaptureStillImageOutput *stillImageOutput;
dispatch_queue_t _videoDataOutputQueue;

NSTimer *_moveAheadTimer;

// UDP Socket for Commands
GCDAsyncUdpSocket *_udpSocket ;

// Multicast UDP Socket for Initial connection.
GCDAsyncUdpSocket *_mudpSocket;

// Stram TCP Server Socket
GCDAsyncSocket *_tcpSocket;

// Stream TCP IP Socket
GCDAsyncSocket *_streamSocket;


- (void)startTimedTask
{
    // Timer seconds.
    _moveAheadTimer = [NSTimer scheduledTimerWithTimeInterval:3.0 target:self selector:@selector(performBackgroundTask) userInfo:nil repeats:YES];
}

- (void)performBackgroundTask
{
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        //Do background work
        
        // Move ahead.
        [ViewController send:_shinkeybotaddress withMessage:[NSString stringWithFormat:@"W"]];
        
        dispatch_async(dispatch_get_main_queue(), ^{
            //Update UI
        });
    });
}
- (IBAction)moveahead:(id)sender {
    
    if (self.aheadswitch.isOn) {
        [self startTimedTask];
        NSLog(@"Moving ahead!");
        
    } else {
        [_moveAheadTimer invalidate];
        NSLog(@"Timer stopped. No more movement for me");
    }
}

//
// Store the IP Address that we obtained in user preferences.
- (void)storeAddress:(NSString*)address {
    // To save data
    NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
    [defaults setObject:address forKey:@"shinkeybotaddress"];
    
    [defaults synchronize];
    NSLog(@"Chunk data saved to defaults.");
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

// Initialize a multicast UDP socket.
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


// EXPERIMENTAL.  Not working very well....
NSMutableData *stream;
NSMutableData *consolidated;

-(void)socket:(GCDAsyncSocket *)sock didReadPartialDataOfLength:(NSUInteger)partialLength tag:(long)tag
{
    NSLog(@"Receiving partial data...");
}


// Convert from NSData to OpenCV Mat colored
- (void) imageFromData: (NSData *) data withSize:(cv::Size) size: (cv::Mat*) img
{
    unsigned char *pix=NULL , *bytes;
    bytes = (unsigned char*)[data bytes];
    NSLog(@"OpenCV Mat size:%d,%d",img->rows, img->cols);
    for (int i = 0; i < size.height; i++)
    {
        for (int j = 0; j < size.width; j++)
        {
            
            pix  = &bytes[i * size.width + j ];
            img->at<unsigned char>(i , 3*j+1 ) = *pix;
            img->at<unsigned char>(i , 3*j+2 ) = *pix;
            img->at<unsigned char>(i , 3*j ) = *pix;
            //img->at<unsigned char>(i,j) = (unsigned char)*pix;
            
            // NSLog(@"%d\n" ,i * size.width*3 + j);
        }
    }
}


- (void)socket:(GCDAsyncSocket *)sock didReadData:(NSData *)data withTag:(long)tag
{
    NSLog(@"Received data so far:%lu", [stream length]);
    
    //[sock readDataWithTimeout:-1 tag:0];
    
    //NSString *msg = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
    //NSLog(@"MSG: %lu",(unsigned long)[msg length]);
    
    /**int offset=0;
    
    unsigned char *bytes = (unsigned char*)[stream bytes];
    if ([stream length]>6)
    for(int i=0;i<[stream length]-6;i++)
    {
        if (bytes[i]==bytes[i+1])
            if (bytes[i+1] == bytes[i+2])
                if (bytes[i+2]==bytes[i+3])
                    if (bytes[i+3]==bytes[i+5])
                        if (bytes[i+5]==32)
                            offset = i;
        
    }
    
    if (offset>0)
    {
        stream = [[NSMutableData alloc] initWithBytes:(bytes+offset) length:[stream length]-offset];
    }**/
    
    
    
    if ([stream length]>(640*480))
    {
        // Check offset.
        //d[0] == d[1] == d[2] == d[3] == d[5] == 32
    
        
        //matC = cv::imdecode(cv::Mat(1, (int)(640*480), CV_8UC1, (void*)aBuffer), CV_LOAD_IMAGE_UNCHANGED);
        consolidated = [stream mutableCopy];
        
        [consolidated setLength:(640*480)];
        stream = [[NSMutableData alloc] initWithCapacity:640*480];

        
    } else {
        [stream appendData:data];
    }
    
    [_streamSocket readDataToLength:640*480 withTimeout:-1 tag:0];
    
}

- (void)socketDidCloseReadStream:(GCDAsyncSocket *)sock
{
    NSLog(@"Stream closed");
}

- (void)socketDidDisconnect:(GCDAsyncSocket *)sock withError:(NSError *)error
{
    NSLog(@"Socket closed");
}

- (void)socket:(GCDAsyncSocket *)sock didAcceptNewSocket:(GCDAsyncSocket *)newSocket
{
    NSLog(@"New Socket Accepted");
    _streamSocket = newSocket;
    
    //[rcvSocket readDataWithTimeout:-1 tag:0];
    [_streamSocket readDataToLength:640*480 withTimeout:-1 tag:0];
}



- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view, typically from a nib.
    
    _shinkeybotaddress = SHINKEYBOTADDRESS;
    //[self recoverStoredAddress];
    
    [_commandText setDelegate:self];
    
    [self setupSocket];
    
    _udpSocket = [[GCDAsyncUdpSocket alloc] initWithDelegate:self delegateQueue:dispatch_get_main_queue()];
    _tcpSocket = [[GCDAsyncSocket alloc] initWithDelegate:self delegateQueue:dispatch_get_main_queue()];
    stream = [[NSMutableData alloc] initWithCapacity:640*480];

    NSError *err = nil;
    if (![_tcpSocket acceptOnPort:10000 error:&err]) {
        NSLog(@"listenSocket failed to accept: %@", err);
    }
    
    // Done configuration.
    
    
    // ----- La primera parte crea los componentes para acceder a la cámara y los asocia a una imagen para provocar visualizaciones.
    // Creamos una Cola sincrónica para la recepción de los mensajes con los frames.
    _videoDataOutputQueue = dispatch_queue_create("com.test.app", NULL); //create a serial queue can either be null or DISPATCH_QUEUE_SERIAL
    
    // Inicializamos el objeto para hacer la captura.
    _captureSession = [[AVCaptureSession alloc] init];
    
    // Creamos un device, un device input asociado.
    AVCaptureDevice * videoDevice = [AVCaptureDevice defaultDeviceWithMediaType:AVMediaTypeVideo];
    if(videoDevice == nil)
        assert(0);
    
    //...y agregamos ese input a la sesión de captura.
    NSError *error;
    AVCaptureDeviceInput *input = [AVCaptureDeviceInput deviceInputWithDevice:videoDevice
                                                                        error:&error];
    if(error)
        assert(0);
    
    [_captureSession addInput:input];
    
    //Agregamos un Layer de Preview que va a estar asociado a un cuadro de imagen.
    _previewLayer = [[AVCaptureVideoPreviewLayer alloc] initWithSession:_captureSession];
    _previewLayer.videoGravity = AVLayerVideoGravityResizeAspectFill;
    
    // Uncomment these lines to have preview.
    /**
    [_previewLayer setFrame:CGRectMake(0, 0,
                                       self.imageView.frame.size.width,
                                       self.imageView.frame.size.height)];
    
    //Finalmente agregamos el layer a la imágen.
    [self.imageView.layer addSublayer:_previewLayer];
    **/
     
    
    // ----- Esta segunda parte, permite sacar una foto.
    
    //stillImageOutput = [[AVCaptureStillImageOutput alloc]init];
    
    //[_captureSession addOutput:stillImageOutput];
    
    
    // ----- La tercera parte, arma la captura de los frames.
    
    AVCaptureVideoDataOutput *videoDataOutput = [AVCaptureVideoDataOutput new];
    
    NSDictionary *newSettings =
    @{ (NSString *)kCVPixelBufferPixelFormatTypeKey : @(kCVPixelFormatType_32BGRA) };
    
    videoDataOutput.videoSettings = newSettings;
    
    // Esto es importante, ya que fuerza descartar aquellos frames que no se pueden procesar por falta de tiempo en el ciclo de procesamiento.
    [videoDataOutput setAlwaysDiscardsLateVideoFrames:YES];
    
    // Usa la cola sincrónica para enviar los frames.
    _videoDataOutputQueue = dispatch_queue_create("VideoDataOutputQueue", DISPATCH_QUEUE_SERIAL);
    [videoDataOutput setSampleBufferDelegate:self queue:_videoDataOutputQueue];
    
    AVCaptureSession *captureSession = _captureSession;
    
    if ( [captureSession canAddOutput:videoDataOutput] )
        [captureSession addOutput:videoDataOutput];
    
    
    //-- Finalmente dispara la captura de la cámara.
    //[_captureSession startRunning];
    
    
}
- (void)viewDidAppear:(BOOL)animated
{
    [super viewWillAppear:animated];
    [_captureSession startRunning];
    
    // So that we can get the picture in portrait mode.
    NSArray *array = [[_captureSession.outputs objectAtIndex:0] connections];
    for (AVCaptureConnection *connection in array)
    {
        connection.videoOrientation = AVCaptureVideoOrientationPortrait;
    }
}


- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}


- (void)viewDidDisappear:(BOOL)animated
{
    [super viewDidDisappear:animated];
    
    [_udpSocket close];
    
    _udpSocket = NULL;
    _streamSocket = NULL;
    _tcpSocket = NULL;
    
}


- (BOOL)textFieldShouldReturn:(UITextField *)textField
{
    [textField resignFirstResponder];
    
    NSLog(@"Send message %@", textField.text);
    
    [ViewController send:_shinkeybotaddress withMessage:textField.text];
    
    return YES;
}

- (IBAction)doRotateLeft:(id)sender {
    [ViewController send:_shinkeybotaddress withMessage:[NSString stringWithFormat:@"UK000"]];
    [ViewController send:_shinkeybotaddress withMessage:[NSString stringWithFormat:@"U 000"]];
}

- (IBAction)doRotateRight:(id)sender {
    [ViewController send:_shinkeybotaddress withMessage:[NSString stringWithFormat:@"UL000"]];
    [ViewController send:_shinkeybotaddress withMessage:[NSString stringWithFormat:@"U 000"]];
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
- (IBAction)doLeft:(id)sender {
    [ViewController send:_shinkeybotaddress withMessage:[NSString stringWithFormat:@"UA000"]];
}


// Método del delegado para capturar frame by frame.
- (void)captureOutput:(AVCaptureOutput *)captureOutput
didOutputSampleBuffer:(CMSampleBufferRef)sampleBuffer
       fromConnection:(AVCaptureConnection *)connection;
{
    // Create a UIImage from the sample buffer data
    UIImage *image = [self imageFromSampleBuffer:sampleBuffer];
    cv::Mat inputMat = [self cvMatFromUIImage:image];
    
    //NSLog(@"Cols %d, Rows %d",inputMat.cols, inputMat.rows);
    
    //[self processImage:inputMat];
    
    cv::Mat greyMat;
    cv::cvtColor(inputMat, greyMat, CV_BGR2GRAY);
    //cv::Mat parm(inputMat.cols, inputMat.rows, CV_8UC4);
    

    [[NSOperationQueue mainQueue] addOperationWithBlock:^
     {
         //self.postviewImage.image = [self UIImageFromCVMat:greyMat];
         self.imageView.image = [self UIImageFromCVMat:greyMat];
     }];
    
    
    //self.imageView.image = image;
}

//TODO: may be remove this code
static double machTimeToSecs(uint64_t time)
{
    mach_timebase_info_data_t timebase;
    mach_timebase_info(&timebase);
    return (double)time * (double)timebase.numer /
    (double)timebase.denom / 1e9;
}

// Macros for time measurements
#if 1
#define TS(name) int64 t_##name = cv::getTickCount()
#define TE(name) printf("TIMER_" #name ": %.2fms\n", \
1000.*((cv::getTickCount() - t_##name) / cv::getTickFrequency()))
#else
#define TS(name)
#define TE(name)
#endif

- (void)processImage:(cv::Mat&)image
{
    cv::Mat inputFrame = image;
    cv::Mat finalFrame;
    
    
    // Apply filter

    uint64_t prevTime = mach_absolute_time();
    // Add fps label to the frame
    uint64_t currTime = mach_absolute_time();
    double timeInSeconds = machTimeToSecs(currTime - prevTime);
    prevTime = currTime;
    double fps = 1.0 / timeInSeconds;
    NSString* fpsString =
    [NSString stringWithFormat:@"FPS = %3.2f", fps];
    cv::putText(finalFrame, [fpsString UTF8String],
                cv::Point(30, 30), cv::FONT_HERSHEY_COMPLEX_SMALL,
                0.8, cv::Scalar::all(255));
    
    finalFrame.copyTo(image);
}

// Utilities
// Create a UIImage from sample buffer data
- (UIImage *) imageFromSampleBuffer:(CMSampleBufferRef) sampleBuffer
{
    //NSLog(@"imageFromSampleBuffer: called");
    // Get a CMSampleBuffer's Core Video image buffer for the media data
    CVImageBufferRef imageBuffer = CMSampleBufferGetImageBuffer(sampleBuffer);
    // Lock the base address of the pixel buffer
    CVPixelBufferLockBaseAddress(imageBuffer, 0);
    
    // Get the number of bytes per row for the pixel buffer
    void *baseAddress = CVPixelBufferGetBaseAddress(imageBuffer);
    
    // Get the number of bytes per row for the pixel buffer
    size_t bytesPerRow = CVPixelBufferGetBytesPerRow(imageBuffer);
    // Get the pixel buffer width and height
    size_t width = CVPixelBufferGetWidth(imageBuffer);
    size_t height = CVPixelBufferGetHeight(imageBuffer);
    
    
    // Create a device-dependent RGB color space
    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
    
    // Create a bitmap graphics context with the sample buffer data
    CGContextRef context = CGBitmapContextCreate(baseAddress, width, height, 8,
                                                 bytesPerRow, colorSpace, kCGBitmapByteOrder32Little | kCGImageAlphaPremultipliedFirst);
    // Create a Quartz image from the pixel data in the bitmap graphics context
    CGImageRef quartzImage = CGBitmapContextCreateImage(context);
    // Unlock the pixel buffer
    CVPixelBufferUnlockBaseAddress(imageBuffer,0);
    
    
    // Free up the context and color space
    CGContextRelease(context);
    CGColorSpaceRelease(colorSpace);
    
    // Create an image object from the Quartz image
    UIImage *image = [UIImage imageWithCGImage:quartzImage];
    
    // Release the Quartz image
    CGImageRelease(quartzImage);
    
    return (image);
}


- (cv::Mat)cvMatFromUIImage:(UIImage *)image
{
    CGColorSpaceRef colorSpace = CGImageGetColorSpace(image.CGImage);
    CGFloat cols = image.size.width;
    CGFloat rows = image.size.height;
    
    cv::Mat cvMat(rows, cols, CV_8UC4); // 8 bits per component, 4 channels (color channels + alpha)
    
    CGContextRef contextRef = CGBitmapContextCreate(cvMat.data,                 // Pointer to  data
                                                    cols,                       // Width of bitmap
                                                    rows,                       // Height of bitmap
                                                    8,                          // Bits per component
                                                    cvMat.step[0],              // Bytes per row
                                                    colorSpace,                 // Colorspace
                                                    kCGImageAlphaNoneSkipLast |
                                                    kCGBitmapByteOrderDefault); // Bitmap info flags
    
    CGContextDrawImage(contextRef, CGRectMake(0, 0, cols, rows), image.CGImage);
    CGContextRelease(contextRef);
    
    return cvMat;
}

- (cv::Mat)cvMatGrayFromUIImage:(UIImage *)image
{
    CGColorSpaceRef colorSpace = CGImageGetColorSpace(image.CGImage);
    CGFloat cols = image.size.width;
    CGFloat rows = image.size.height;
    
    cv::Mat cvMat(rows, cols, CV_8UC1); // 8 bits per component, 1 channels
    
    CGContextRef contextRef = CGBitmapContextCreate(cvMat.data,                 // Pointer to data
                                                    cols,                       // Width of bitmap
                                                    rows,                       // Height of bitmap
                                                    8,                          // Bits per component
                                                    cvMat.step[0],              // Bytes per row
                                                    colorSpace,                 // Colorspace
                                                    kCGImageAlphaNoneSkipLast |
                                                    kCGBitmapByteOrderDefault); // Bitmap info flags
    
    CGContextDrawImage(contextRef, CGRectMake(0, 0, cols, rows), image.CGImage);
    CGContextRelease(contextRef);
    
    return cvMat;
}


//
// Receives the buffer information and and generates the OpenCV matrix to draw the transmitted image.
//
//
-(UIImage *)UIImageFromCVMat:(cv::Mat)cvMat
{
    //cv::transpose(cvMat, cvMatDst);
    //flip(cvMatDst, cvMatDst,1);
    
    cv::Mat cvs(640, 480, CV_8UC4);
    Canny( cvMat, cvMat, 50, 150, 3);
    
    
    if ([consolidated length]>=640*480)
        [self imageFromData:consolidated withSize:cv::Size(640,480) :&cvs];
    
    if ([consolidated length]>=640*480)
    {
        for(int i=0;i<640;i++)
            for(int j=0;j<480;j++)
            {
    //            cvs.at<unsigned char>(i,j) = 120;
            }
    }
    
    
    cvMat = cvs;
    
    NSData *data = [NSData dataWithBytes:cvMat.data length:cvMat.elemSize()*cvMat.total()];
    
    
    CGColorSpaceRef colorSpace;
    
    if (cvMat.elemSize() == 1) {
        colorSpace = CGColorSpaceCreateDeviceGray();
    } else {
        colorSpace = CGColorSpaceCreateDeviceRGB();
    }
    
    CGDataProviderRef provider = CGDataProviderCreateWithCFData((__bridge CFDataRef)data);
    
    //NSLog(@"Cols %d and rows %d:", cvMat.cols, cvMat.rows);
    
    // Creating CGImage from cv::Mat
    CGImageRef imageRef = CGImageCreate(cvMat.cols,                                 //width
                                        cvMat.rows,                                 //height
                                        8,                                          //bits per component
                                        8 * cvMat.elemSize(),                       //bits per pixel
                                        cvMat.step[0],                            //bytesPerRow
                                        colorSpace,                                 //colorspace
                                        kCGImageAlphaNone|kCGBitmapByteOrderDefault,// bitmap info
                                        provider,                                   //CGDataProviderRef
                                        NULL,                                       //decode
                                        false,                                      //should interpolate
                                        kCGRenderingIntentDefault                   //intent
                                        );
    
    
    // Getting UIImage from CGImage
    UIImage *finalImage = [UIImage imageWithCGImage:imageRef];
    CGImageRelease(imageRef);
    CGDataProviderRelease(provider);
    CGColorSpaceRelease(colorSpace);
    
    return finalImage;
}



@end
