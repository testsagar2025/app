import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:hive_flutter/hive_flutter.dart';

import 'screens/splash_screen.dart';
import 'screens/home_screen.dart';
import 'screens/daily_brief_screen.dart';
import 'screens/capture_screen.dart';
import 'screens/progress_screen.dart';
import 'services/offline_storage_service.dart';
import 'utils/theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Hive for local storage
  await Hive.initFlutter();
  await OfflineStorageService.initialize();
  
  // Lock orientation to portrait
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  
  runApp(const SetuApp());
}

class SetuApp extends StatelessWidget {
  const SetuApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ScreenUtilInit(
      designSize: const Size(375, 812),
      minTextAdapt: true,
      splitScreenMode: true,
      builder: (context, child) {
        return MaterialApp(
          title: 'Setu',
          debugShowCheckedModeBanner: false,
          theme: SetuTheme.lightTheme,
          darkTheme: SetuTheme.darkTheme,
          themeMode: ThemeMode.light,
          initialRoute: '/',
          routes: {
            '/': (context) => const SplashScreen(),
            '/home': (context) => const HomeScreen(),
            '/daily-brief': (context) => const DailyBriefScreen(),
            '/capture': (context) => const CaptureScreen(),
            '/progress': (context) => const ProgressScreen(),
          },
        );
      },
    );
  }
}
