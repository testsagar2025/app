import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:intl/intl.dart';

import '../services/offline_storage_service.dart';
import '../utils/theme.dart';
import 'daily_brief_screen.dart';
import 'capture_screen.dart';
import 'progress_screen.dart';

/// Home Screen - Main dashboard
/// Shows quick overview and navigation to key features
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;
  
  final List<Widget> _screens = [
    const _HomeDashboard(),
    const DailyBriefScreen(),
    const CaptureScreen(),
    const ProgressScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: SetuTheme.surface,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, -4),
            ),
          ],
        ),
        child: SafeArea(
          child: Padding(
            padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 8.h),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildNavItem(Icons.home_rounded, 'Home', 0),
                _buildNavItem(Icons.calendar_today_rounded, 'Today', 1),
                _buildNavItem(Icons.add_circle, 'Capture', 2, isCenter: true),
                _buildNavItem(Icons.trending_up_rounded, 'Progress', 3),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem(IconData icon, String label, int index, {bool isCenter = false}) {
    final isSelected = _currentIndex == index;
    
    if (isCenter) {
      return GestureDetector(
        onTap: () => setState(() => _currentIndex = index),
        child: Container(
          width: 56.w,
          height: 56.w,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [SetuTheme.primary, SetuTheme.primaryDark],
            ),
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: SetuTheme.primary.withOpacity(0.4),
                blurRadius: 12,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Icon(
            icon,
            color: SetuTheme.textInverse,
            size: 28.sp,
          ),
        ),
      );
    }
    
    return GestureDetector(
      onTap: () => setState(() => _currentIndex = index),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            color: isSelected ? SetuTheme.primary : SetuTheme.textTertiary,
            size: 24.sp,
          ),
          SizedBox(height: 4.h),
          Text(
            label,
            style: TextStyle(
              fontSize: 11.sp,
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
              color: isSelected ? SetuTheme.primary : SetuTheme.textTertiary,
            ),
          ),
        ],
      ),
    );
  }
}

/// Home Dashboard - Main overview
class _HomeDashboard extends StatefulWidget {
  const _HomeDashboard();

  @override
  State<_HomeDashboard> createState() => _HomeDashboardState();
}

class _HomeDashboardState extends State<_HomeDashboard> {
  Map<String, dynamic>? _stats;

  @override
  void initState() {
    super.initState();
    _loadStats();
  }

  void _loadStats() {
    setState(() {
      _stats = OfflineStorageService.getStatistics();
    });
  }

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final dateFormat = DateFormat('EEEE, MMMM d');
    
    return SafeArea(
      child: CustomScrollView(
        slivers: [
          // Header
          SliverToBoxAdapter(
            child: Padding(
              padding: EdgeInsets.all(20.w),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    dateFormat.format(now),
                    style: TextStyle(
                      fontSize: 14.sp,
                      color: SetuTheme.textSecondary,
                    ),
                  ),
                  SizedBox(height: 4.h),
                  Text(
                    'Welcome back, Aarav! 👋',
                    style: TextStyle(
                      fontSize: 24.sp,
                      fontWeight: FontWeight.bold,
                      color: SetuTheme.textPrimary,
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Quick Stats
          SliverToBoxAdapter(
            child: Padding(
              padding: EdgeInsets.symmetric(horizontal: 20.w),
              child: Row(
                children: [
                  Expanded(
                    child: _buildStatCard(
                      icon: Icons.check_circle,
                      value: '${_stats?['completedTasks'] ?? 0}',
                      label: 'Tasks Done',
                      color: SetuTheme.success,
                    ),
                  ),
                  SizedBox(width: 12.w),
                  Expanded(
                    child: _buildStatCard(
                      icon: Icons.timer,
                      value: '${(_stats?['totalStudyMinutes'] ?? 0) ~/ 60}h',
                      label: 'Study Time',
                      color: SetuTheme.primary,
                    ),
                  ),
                  SizedBox(width: 12.w),
                  Expanded(
                    child: _buildStatCard(
                      icon: Icons.local_fire_department,
                      value: '12',
                      label: 'Day Streak',
                      color: SetuTheme.accent,
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Quick Actions
          SliverToBoxAdapter(
            child: Padding(
              padding: EdgeInsets.fromLTRB(20.w, 32.h, 20.w, 16.h),
              child: Text(
                'Quick Actions',
                style: TextStyle(
                  fontSize: 18.sp,
                  fontWeight: FontWeight.w600,
                  color: SetuTheme.textPrimary,
                ),
              ),
            ),
          ),

          SliverToBoxAdapter(
            child: Padding(
              padding: EdgeInsets.symmetric(horizontal: 20.w),
              child: Column(
                children: [
                  _buildActionCard(
                    icon: Icons.calendar_today,
                    title: 'View Today\'s Plan',
                    subtitle: '3 must-do tasks waiting',
                    color: SetuTheme.primary,
                    onTap: () {
                      // Navigate to daily brief
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => const DailyBriefScreen(),
                        ),
                      );
                    },
                  ),
                  SizedBox(height: 12.h),
                  _buildActionCard(
                    icon: Icons.camera_alt,
                    title: 'Capture School Session',
                    subtitle: 'Tell Setu what happened today',
                    color: SetuTheme.secondary,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => const CaptureScreen(),
                        ),
                      );
                    },
                  ),
                  SizedBox(height: 12.h),
                  _buildActionCard(
                    icon: Icons.trending_up,
                    title: 'Check Progress',
                    subtitle: 'See your learning journey',
                    color: SetuTheme.accent,
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => const ProgressScreen(),
                        ),
                      );
                    },
                  ),
                ],
              ),
            ),
          ),

          // Today's Focus
          SliverToBoxAdapter(
            child: Padding(
              padding: EdgeInsets.fromLTRB(20.w, 32.h, 20.w, 16.h),
              child: Text(
                'Today\'s Focus',
                style: TextStyle(
                  fontSize: 18.sp,
                  fontWeight: FontWeight.w600,
                  color: SetuTheme.textPrimary,
                ),
              ),
            ),
          ),

          SliverToBoxAdapter(
            child: Padding(
              padding: EdgeInsets.symmetric(horizontal: 20.w),
              child: Container(
                padding: EdgeInsets.all(20.w),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      SetuTheme.physics.withOpacity(0.2),
                      SetuTheme.physics.withOpacity(0.05),
                    ],
                  ),
                  borderRadius: BorderRadius.circular(20.r),
                  border: Border.all(
                    color: SetuTheme.physics.withOpacity(0.3),
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          padding: EdgeInsets.all(10.w),
                          decoration: BoxDecoration(
                            color: SetuTheme.physics.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(12.r),
                          ),
                          child: Text(
                            '⚛️',
                            style: TextStyle(fontSize: 24.sp),
                          ),
                        ),
                        SizedBox(width: 14.w),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Physics',
                                style: TextStyle(
                                  fontSize: 16.sp,
                                  fontWeight: FontWeight.w600,
                                  color: SetuTheme.textPrimary,
                                ),
                              ),
                              Text(
                                'Rotational Motion',
                                style: TextStyle(
                                  fontSize: 14.sp,
                                  color: SetuTheme.textSecondary,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 16.h),
                    Text(
                      'Working on: Torque, Angular Momentum',
                      style: TextStyle(
                        fontSize: 13.sp,
                        color: SetuTheme.textSecondary,
                      ),
                    ),
                    SizedBox(height: 8.h),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(6.r),
                      child: LinearProgressIndicator(
                        value: 0.62,
                        backgroundColor: SetuTheme.surface,
                        valueColor: AlwaysStoppedAnimation<Color>(SetuTheme.physics),
                        minHeight: 8.h,
                      ),
                    ),
                    SizedBox(height: 8.h),
                    Text(
                      '62% complete',
                      style: TextStyle(
                        fontSize: 12.sp,
                        color: SetuTheme.textTertiary,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

          // Bottom padding
          SliverToBoxAdapter(
            child: SizedBox(height: 40.h),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard({
    required IconData icon,
    required String value,
    required String label,
    required Color color,
  }) {
    return Container(
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        color: SetuTheme.surface,
        borderRadius: BorderRadius.circular(16.r),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Icon(
            icon,
            color: color,
            size: 28.sp,
          ),
          SizedBox(height: 8.h),
          Text(
            value,
            style: TextStyle(
              fontSize: 20.sp,
              fontWeight: FontWeight.bold,
              color: SetuTheme.textPrimary,
            ),
          ),
          SizedBox(height: 4.h),
          Text(
            label,
            style: TextStyle(
              fontSize: 11.sp,
              color: SetuTheme.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16.r),
      child: Container(
        padding: EdgeInsets.all(16.w),
        decoration: BoxDecoration(
          color: SetuTheme.surface,
          borderRadius: BorderRadius.circular(16.r),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              width: 48.w,
              height: 48.w,
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12.r),
              ),
              child: Icon(
                icon,
                color: color,
                size: 24.sp,
              ),
            ),
            SizedBox(width: 16.w),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontSize: 15.sp,
                      fontWeight: FontWeight.w600,
                      color: SetuTheme.textPrimary,
                    ),
                  ),
                  SizedBox(height: 4.h),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 13.sp,
                      color: SetuTheme.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              Icons.arrow_forward_ios,
              size: 16.sp,
              color: SetuTheme.textTertiary,
            ),
          ],
        ),
      ),
    );
  }
}
