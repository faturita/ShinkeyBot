//
//  ViewController.h
//  ShinkeyBotController
//
//  Created by Rodrigo Ramele on 10/10/16.
//  Copyright © 2016 Baufest. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <opencv2/opencv.hpp>

@interface ViewController : UIViewController <UITextFieldDelegate,AVCaptureVideoDataOutputSampleBufferDelegate>

@property (strong, atomic) NSString *shinkeybotaddress;

@end

