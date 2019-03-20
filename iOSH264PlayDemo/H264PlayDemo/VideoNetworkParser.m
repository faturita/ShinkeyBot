//
//  VideoNetworkParser.m
//  H264PlayDemo
//
//  Created by Rodrigo Ramele on 10/14/17.
//  Copyright © 2017 王爽. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "VideoNetworkParser.h"

@implementation VideoNetworkParser

- (NSInputStream*)openInputStream:(NSString *)fileName
{
    NSLog(@"%@", fileName);
    
    NSString *urlStr = @"10.17.10.107";
    
    urlStr = fileName;
    
    if (![urlStr isEqualToString:@""]) {
        NSURL *website = [NSURL URLWithString:urlStr];
        if (!website) {
            NSLog(@"%@ is not a valid URL", urlStr);
            return NULL;
        }
        
        CFReadStreamRef readStream;
        CFWriteStreamRef writeStream;
        CFStreamCreatePairWithSocketToHost(NULL, (__bridge CFStringRef)urlStr, 10000, &readStream, &writeStream);
        
        NSInputStream *inputStream = (__bridge_transfer NSInputStream *)readStream;
        NSOutputStream *outputStream = (__bridge_transfer NSOutputStream *)writeStream;
        //[inputStream setDelegate:self];
        //[outputStream setDelegate:self];
        //[inputStream scheduleInRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
        //[outputStream scheduleInRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
        //[inputStream open];
        //[outputStream open];
        
        /* Store a reference to the input and output streams so that
         they don't go away.... */
        
        return inputStream;
    }
    return NULL;
}

@end
