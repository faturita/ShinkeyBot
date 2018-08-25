#import <Foundation/Foundation.h>
#include "VideoFileParser.h"

const uint8_t KStartCode[4] = {0, 0, 0, 1};

@implementation VideoPacket
- (instancetype)initWithSize:(NSInteger)size
{
    self = [super init];
    self.buffer = malloc(size);
    self.size = size;
    
    return self;
}

-(void)dealloc
{
    free(self.buffer);
}
@end

@interface VideoFileParser ()
{
    uint8_t *_buffer;
    NSInteger _bufferSize;
    NSInteger _bufferCap;
}
@property  NSString *fileName;
@property  NSInputStream *fileStream;
@end

@implementation VideoFileParser

- (NSInputStream*)fromNetwork
{
    NSString *urlStr = @"192.168.0.105";
    
    if (![urlStr isEqualToString:@""]) {
        NSURL *website = [NSURL URLWithString:urlStr];
        if (!website) {
            NSLog(@"%@ is not a valid URL", urlStr);
            return NULL;
        }
        
        CFReadStreamRef readStream;
        CFWriteStreamRef writeStream;
        CFStreamCreatePairWithSocketToHost(NULL, (__bridge CFStringRef)@"192.168.0.105", 10000, &readStream, &writeStream);
        
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

-(NSInputStream*)openInputStream:(NSString *)fileName
{
    return [NSInputStream inputStreamWithFileAtPath:fileName];
}

-(void)prepare
{
    _bufferSize = 0;
    _bufferCap = 512 * 1024;
    _buffer = malloc(_bufferCap);
}

-(BOOL)open:(NSString *)fileName
{
    [self prepare];
    
    self.fileName = fileName;
    self.fileStream = [self openInputStream:fileName];

    [self.fileStream open];

    return YES;
}

-(VideoPacket*)nextPacket
{
    if (self.fileStream.hasBytesAvailable)
    {
        NSLog(@"Buffer is empty");
    }
    
    if(_bufferSize < _bufferCap && self.fileStream.hasBytesAvailable) {
        NSInteger readBytes = [self.fileStream read:_buffer + _bufferSize maxLength:_bufferCap - _bufferSize];
        _bufferSize += readBytes;
    }
    
    if(_bufferSize >= 5) {
        uint8_t *bufferBegin = _buffer + 4;
        uint8_t *bufferEnd = _buffer + _bufferSize;
        while(bufferBegin != bufferEnd) {
            if(*bufferBegin == 0x01) {
                if(memcmp(bufferBegin - 3, KStartCode, 4) == 0) {
                    NSInteger packetSize = bufferBegin - _buffer - 3;
                    VideoPacket *vp = [[VideoPacket alloc] initWithSize:packetSize];
                    memcpy(vp.buffer, _buffer, packetSize);
                    
                    NSLog(@"Reading %d bytes", packetSize);
                    
                    memmove(_buffer, _buffer + packetSize, _bufferSize - packetSize);
                    _bufferSize -= packetSize;
                    
                    return vp;
                }
            }
            ++bufferBegin;
        }
    }

    return nil;
}

-(void)close
{
    free(_buffer);
    [self.fileStream close];
}

@end
