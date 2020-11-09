// Clang 5 doesn't understand the macOS 11 SDK's availability macros; replace them with our own simpler ones.
#define __OS_AVAILABILITY__
#define API_AVAILABLE(...)
#define API_UNAVAILABLE(...)
#define API_UNAVAILABLE_BEGIN(...)
#define API_UNAVAILABLE_END
#define API_DEPRECATED(message, ...) __attribute__((deprecated(message)))
#define API_DEPRECATED_WITH_REPLACEMENT(replacement, ...) __attribute__((deprecated("Deprecated; repaced by " replacement)))
#define UT_AVAILABLE_BEGIN
#define UT_AVAILABLE_END

#include <stdio.h>
#import <HapInAVFoundation/HapInAVFoundation.h>

int main()
{
	HapEncoderFrame *hef = [HapEncoderFrame createWithPresentationTime:kCMTimeZero];
	if (!hef)
	{
		printf("Unable to initialize HapInAVFoundation.\n");
		return -1;
	}

	printf("Successfully initialized HapInAVFoundation.\n");

	return 0;
}
