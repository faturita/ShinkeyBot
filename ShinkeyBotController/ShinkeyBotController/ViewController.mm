//
//  ViewController.m
//  ShinkeyBotController
//
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
#import <opencv2/opencv.hpp>

#import <mach/mach_time.h>


@interface ViewController ()
@property (weak, nonatomic) IBOutlet UIImageView *imageView;
@property (weak, nonatomic) IBOutlet UITextField *commandText;
@end

@implementation ViewController
AVCaptureVideoPreviewLayer *_previewLayer;
AVCaptureSession *_captureSession;
AVCaptureStillImageOutput *stillImageOutput;
dispatch_queue_t _videoDataOutputQueue;



-(IBAction) captureNow
{
    AVCaptureConnection *videoConnection = nil;
    for (AVCaptureConnection *connection in stillImageOutput.connections)
    {
        for (AVCaptureInputPort *port in [connection inputPorts])
        {
            if ([[port mediaType] isEqual:AVMediaTypeVideo] )
            {
                videoConnection = connection;
                break;
            }
        }
        if (videoConnection) { break; }
    }
    
    
    NSLog(@"about to request a capture from: %@", stillImageOutput);
    [stillImageOutput captureStillImageAsynchronouslyFromConnection:videoConnection completionHandler: ^(CMSampleBufferRef imageSampleBuffer, NSError *error)
     {
         /**
         CFDictionaryRef exifAttachments = CMGetAttachment( imageSampleBuffer, kCGImagePropertyExifDictionary, NULL);
         if (exifAttachments)
         {
             // Do something with the attachments.
             NSLog(@"attachements: %@", exifAttachments);
         }
         else
             NSLog(@"no attachments");
         **/
         
         NSData *imageData = [AVCaptureStillImageOutput jpegStillImageNSDataRepresentation:imageSampleBuffer];
         UIImage *image = [[UIImage alloc] initWithData:imageData];
         
         cv::Mat inputMat = [self cvMatFromUIImage:image];
         
         NSLog(@"Cols %d, Rows %d",inputMat.cols, inputMat.rows);
         
         
         //cv::Mat greyMat;
         //cv::cvtColor(inputMat, greyMat, CV_BGR2GRAY);
         
         //self.imageView.image = [self UIImageFromCVMat:inputMat];
         
         
         
         self.imageView.image = image;
     }];
}


- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view, typically from a nib.
    
    [_commandText setDelegate:self];
    
}


- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

+ (void)send:(NSString*)host withMessage:(NSString*)message
{
    [self send:host withPort:10001 withMessage:message];
}

- (void)captureOutput:(AVCaptureOutput *)captureOutput
didOutputSampleBuffer:(CMSampleBufferRef)sampleBuffer
       fromConnection:(AVCaptureConnection *)connection;
{
    // Create a UIImage from the sample buffer data
    UIImage *image = [self imageFromSampleBuffer:sampleBuffer];
    
    
    cv::Mat inputMat = [self cvMatFromUIImage:image];
    
    NSLog(@"Cols %d, Rows %d",inputMat.cols, inputMat.rows);
    
    //[self processImage:inputMat];
    
    cv::Mat greyMat;
    cv::cvtColor(inputMat, greyMat, CV_BGR2GRAY);
    
    self.imageView.image = [self UIImageFromCVMat:greyMat];
    
    
    
    //self.imageView.image = image;
}

// Create a UIImage from sample buffer data
- (UIImage *) imageFromSampleBuffer:(CMSampleBufferRef) sampleBuffer
{
    NSLog(@"imageFromSampleBuffer: called");
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

+ (void)send:(NSString*)host withPort:(int)port withMessage:(NSString *)message
{
    GCDAsyncUdpSocket *udpSocket ; // create this first part as a global variable
    udpSocket = [[GCDAsyncUdpSocket alloc] initWithDelegate:self delegateQueue:dispatch_get_main_queue()];
    
    NSData* data = [[NSString stringWithString:message] dataUsingEncoding:NSASCIIStringEncoding];
    
    NSLog(@"Send message %@", message);
    
    [udpSocket sendData:data toHost:host port:port withTimeout:-1 tag:1];
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

-(UIImage *)UIImageFromCVMat:(cv::Mat)cvMat
{
    NSData *data = [NSData dataWithBytes:cvMat.data length:cvMat.elemSize()*cvMat.total()];
    CGColorSpaceRef colorSpace;
    
    if (cvMat.elemSize() == 1) {
        colorSpace = CGColorSpaceCreateDeviceGray();
    } else {
        colorSpace = CGColorSpaceCreateDeviceRGB();
    }
    
    CGDataProviderRef provider = CGDataProviderCreateWithCFData((__bridge CFDataRef)data);
    
    NSLog(@"Cols %d and rows %d:", cvMat.cols, cvMat.rows);
    
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

- (IBAction)doUp:(id)sender {
    [ViewController send:@"192.168.0.110" withMessage:[NSString stringWithFormat:@"2"]];
}
- (IBAction)doDown:(id)sender {
    [ViewController send:@"192.168.0.110" withMessage:[NSString stringWithFormat:@"3"]];
}

- (IBAction)doRight:(id)sender {
    [ViewController send:@"192.168.0.110" withMessage:[NSString stringWithFormat:@"4"]];
}
- (IBAction)doLeft:(id)sender {
    [ViewController send:@"192.168.0.110" withMessage:[NSString stringWithFormat:@"5"]];
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


- (BOOL)textFieldShouldReturn:(UITextField *)textField
{
    [textField resignFirstResponder];
    
    NSLog(@"Send message %@", textField.text);
    
    [ViewController send:@"192.168.0.110" withMessage:textField.text];
    
    return YES;
}
@end
