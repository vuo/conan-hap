from conans import ConanFile, tools
import os

class HapConan(ConanFile):
    name = 'hap'

    source_version = '1.5.3'
    package_version = '1'
    version = '%s-%s' % (source_version, package_version)

    build_requires = (
        'llvm/5.0.2-1@vuo/stable',
        'macos-sdk/11.0-0@vuo/stable',
    )
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/Vidvox/hap-in-avfoundation'
    license = 'https://github.com/Vidvox/hap-in-avfoundation/blob/master/LICENSE'
    source_dir = 'hap-in-avfoundation-%s' % source_version

    install_x86_dir = '_install_x86'
    install_arm_dir = '_install_arm'
    install_universal_dir = '_install_universal'

    exports_sources = '*.patch'

    def source(self):
        tools.get('https://github.com/Vidvox/hap-in-avfoundation/archive/%s.tar.gz' % self.source_version,
                  sha256='0afa1468b940fce1390691f689ffea732217fb1efe6845137710f107ea3b0cb4')

        tools.patch(patch_file='arm64.patch', base_path=self.source_dir)

        self.run('mv %s/LICENSE %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        tools.mkdir(self.install_x86_dir)
        tools.mkdir(self.install_arm_dir)
        with tools.chdir(self.source_dir):
            header_search_paths = 'HEADER_SEARCH_PATHS="%s %s"' % (
                "%s/external/snappy/snappy-source" % os.getcwd(),
                "%s/external/squish/squish-source" % os.getcwd(),
            )
            self.output.info("=== Build for x86_64 ===")
            self.run('xcodebuild -quiet -target HapInAVFoundation ARCHS="x86_64" VALID_ARCHS="x86_64" MACOSX_DEPLOYMENT_TARGET=10.11 CODE_SIGN_IDENTITY="" %s' % header_search_paths)
            self.run('cp -a build/Release/HapInAVFoundation.framework ../%s' % self.install_x86_dir)

            self.output.info("=== Build for arm64 ===")
            self.run('xcodebuild -quiet -target HapInAVFoundation ARCHS="arm64" VALID_ARCHS="arm64" MACOSX_DEPLOYMENT_TARGET=10.11 CODE_SIGN_IDENTITY="" GCC_PREPROCESSOR_DEFINITIONS="SQUISH_USE_SSE=0" %s' % header_search_paths)
            self.run('cp -a build/Release/HapInAVFoundation.framework ../%s' % self.install_arm_dir)

        self.run('cp -a %s %s' % (self.install_x86_dir, self.install_universal_dir))

        self.run('lipo -create %s/HapInAVFoundation.framework/Versions/A/HapInAVFoundation %s/HapInAVFoundation.framework/Versions/A/HapInAVFoundation -output %s/HapInAVFoundation.framework/Versions/A/HapInAVFoundation' % (self.install_x86_dir, self.install_arm_dir, self.install_universal_dir))
        self.run('lipo -create %s/HapInAVFoundation.framework/Versions/A/Frameworks/libsnappy.dylib %s/HapInAVFoundation.framework/Versions/A/Frameworks/libsnappy.dylib -output %s/HapInAVFoundation.framework/Versions/A/Frameworks/libsnappy.dylib' % (self.install_x86_dir, self.install_arm_dir, self.install_universal_dir))
        self.run('lipo -create %s/HapInAVFoundation.framework/Versions/A/Frameworks/libsquish.dylib %s/HapInAVFoundation.framework/Versions/A/Frameworks/libsquish.dylib -output %s/HapInAVFoundation.framework/Versions/A/Frameworks/libsquish.dylib' % (self.install_x86_dir, self.install_arm_dir, self.install_universal_dir))

        self.run('codesign --sign - %s/HapInAVFoundation.framework/Versions/A/Frameworks/libsnappy.dylib' % self.install_universal_dir)
        self.run('codesign --sign - %s/HapInAVFoundation.framework/Versions/A/Frameworks/libsquish.dylib' % self.install_universal_dir)
        self.run('codesign --sign - %s/HapInAVFoundation.framework'                                       % self.install_universal_dir)

        # HapInAVFoundation.framework is missing the root Frameworks symlink.
        # Since it references its inner dylibs paths relative to the root of the framework,
        # add the symlink so it can find them.
        self.run('ln -s Versions/Current/Frameworks %s/HapInAVFoundation.framework' % self.install_universal_dir)

    def package(self):
        self.copy('*', src='%s/HapInAVFoundation.framework' % self.install_universal_dir, dst='lib/HapInAVFoundation.framework', symlinks=True)
        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.frameworkdirs = ['%s/lib' % self.package_folder]
        self.cpp_info.frameworks = ['HapInAVFoundation']
