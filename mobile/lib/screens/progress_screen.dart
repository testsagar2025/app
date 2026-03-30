import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:fl_chart/fl_chart.dart';

import '../services/offline_storage_service.dart';
import '../models/task_model.dart';
import '../utils/theme.dart';

/// Progress Screen - Shows learning analytics and insights
class ProgressScreen extends StatefulWidget {
  const ProgressScreen({super.key});

  @override
  State<ProgressScreen> createState() => _ProgressScreenState();
}

class _ProgressScreenState extends State<ProgressScreen> {
  List<ConceptMastery> _concepts = [];
  Map<String, dynamic>? _stats;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    
    _concepts = OfflineStorageService.getAllConcepts();
    _stats = OfflineStorageService.getStatistics();
    
    // If no data, generate mock data
    if (_concepts.isEmpty) {
      _generateMockConcepts();
    }
    
    setState(() => _isLoading = false);
  }

  void _generateMockConcepts() {
    _concepts = [
      ConceptMastery(
        conceptId: 'angular_velocity',
        exposureCount: 5,
        correctApplicationRate: 0.85,
        confidenceScore: 0.82,
        masteryLevel: 'strong',
      ),
      ConceptMastery(
        conceptId: 'moment_of_inertia',
        exposureCount: 3,
        correctApplicationRate: 0.60,
        confidenceScore: 0.55,
        errorCount: 2,
        errorPatterns: ['formula_recall'],
        specificWeaknesses: ['forgets_factor_of_half_for_disc'],
        masteryLevel: 'moderate',
      ),
      ConceptMastery(
        conceptId: 'torque',
        exposureCount: 4,
        correctApplicationRate: 0.45,
        confidenceScore: 0.40,
        errorCount: 5,
        errorPatterns: ['sign_convention', 'axis_selection'],
        specificWeaknesses: ['sign_confusion', 'clockwise_vs_anticlockwise'],
        masteryLevel: 'weak',
      ),
      ConceptMastery(
        conceptId: 'angular_momentum',
        exposureCount: 2,
        correctApplicationRate: 0.30,
        confidenceScore: 0.25,
        masteryLevel: 'weak',
      ),
      ConceptMastery(
        conceptId: 'conservation_laws',
        exposureCount: 0,
        masteryLevel: 'not_started',
      ),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SetuTheme.background,
      appBar: AppBar(
        title: const Text('Your Progress'),
        elevation: 0,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : CustomScrollView(
              slivers: [
                // Overall Stats
                SliverToBoxAdapter(
                  child: _buildOverallStats(),
                ),

                // Weekly Activity Chart
                SliverToBoxAdapter(
                  child: _buildWeeklyChart(),
                ),

                // Subject Breakdown
                SliverToBoxAdapter(
                  child: _buildSubjectBreakdown(),
                ),

                // Concept Mastery
                SliverToBoxAdapter(
                  child: Padding(
                    padding: EdgeInsets.fromLTRB(20.w, 32.h, 20.w, 16.h),
                    child: Text(
                      'Concept Mastery',
                      style: TextStyle(
                        fontSize: 18.sp,
                        fontWeight: FontWeight.w600,
                        color: SetuTheme.textPrimary,
                      ),
                    ),
                  ),
                ),

                SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, index) {
                      final concept = _concepts[index];
                      return _buildConceptCard(concept);
                    },
                    childCount: _concepts.length,
                  ),
                ),

                // Weak Areas Focus
                SliverToBoxAdapter(
                  child: _buildWeakAreasSection(),
                ),

                // Bottom padding
                SliverToBoxAdapter(
                  child: SizedBox(height: 40.h),
                ),
              ],
            ),
    );
  }

  Widget _buildOverallStats() {
    return Padding(
      padding: EdgeInsets.all(20.w),
      child: Row(
        children: [
          Expanded(
            child: _buildStatBox(
              'Concepts\nMastered',
              '${_concepts.where((c) => c.masteryLevel == 'mastered').length}',
              SetuTheme.success,
            ),
          ),
          SizedBox(width: 12.w),
          Expanded(
            child: _buildStatBox(
              'Strong\nAreas',
              '${_concepts.where((c) => c.masteryLevel == 'strong').length}',
              SetuTheme.primary,
            ),
          ),
          SizedBox(width: 12.w),
          Expanded(
            child: _buildStatBox(
              'Needs\nWork',
              '${_concepts.where((c) => c.masteryLevel == 'weak').length}',
              SetuTheme.warning,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatBox(String label, String value, Color color) {
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
          Text(
            value,
            style: TextStyle(
              fontSize: 28.sp,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          SizedBox(height: 8.h),
          Text(
            label,
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 11.sp,
              color: SetuTheme.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWeeklyChart() {
    return Padding(
      padding: EdgeInsets.symmetric(horizontal: 20.w),
      child: Container(
        padding: EdgeInsets.all(20.w),
        decoration: BoxDecoration(
          color: SetuTheme.surface,
          borderRadius: BorderRadius.circular(20.r),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Weekly Activity',
              style: TextStyle(
                fontSize: 16.sp,
                fontWeight: FontWeight.w600,
                color: SetuTheme.textPrimary,
              ),
            ),
            SizedBox(height: 8.h),
            Text(
              'Tasks completed this week',
              style: TextStyle(
                fontSize: 13.sp,
                color: SetuTheme.textSecondary,
              ),
            ),
            SizedBox(height: 20.h),
            SizedBox(
              height: 180.h,
              child: BarChart(
                BarChartData(
                  alignment: BarChartAlignment.spaceAround,
                  maxY: 10,
                  barTouchData: BarTouchData(enabled: false),
                  titlesData: FlTitlesData(
                    show: true,
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (value, meta) {
                          const days = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
                          return Text(
                            days[value.toInt()],
                            style: TextStyle(
                              fontSize: 12.sp,
                              color: SetuTheme.textSecondary,
                            ),
                          );
                        },
                      ),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    topTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    rightTitles: AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                  ),
                  gridData: FlGridData(show: false),
                  borderData: FlBorderData(show: false),
                  barGroups: [
                    _buildBarGroup(0, 5, SetuTheme.primary),
                    _buildBarGroup(1, 7, SetuTheme.primary),
                    _buildBarGroup(2, 4, SetuTheme.primary),
                    _buildBarGroup(3, 8, SetuTheme.success),
                    _buildBarGroup(4, 6, SetuTheme.primary),
                    _buildBarGroup(5, 3, SetuTheme.warning),
                    _buildBarGroup(6, 2, SetuTheme.warning),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  BarChartGroupData _buildBarGroup(int x, int y, Color color) {
    return BarChartGroupData(
      x: x,
      barRods: [
        BarChartRodData(
          toY: y.toDouble(),
          color: color,
          width: 20.w,
          borderRadius: BorderRadius.circular(6.r),
        ),
      ],
    );
  }

  Widget _buildSubjectBreakdown() {
    return Padding(
      padding: EdgeInsets.fromLTRB(20.w, 24.h, 20.w, 0),
      child: Container(
        padding: EdgeInsets.all(20.w),
        decoration: BoxDecoration(
          color: SetuTheme.surface,
          borderRadius: BorderRadius.circular(20.r),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Subject Progress',
              style: TextStyle(
                fontSize: 16.sp,
                fontWeight: FontWeight.w600,
                color: SetuTheme.textPrimary,
              ),
            ),
            SizedBox(height: 20.h),
            _buildSubjectRow('Physics', 0.62, SetuTheme.physics),
            SizedBox(height: 16.h),
            _buildSubjectRow('Chemistry', 0.75, SetuTheme.chemistry),
            SizedBox(height: 16.h),
            _buildSubjectRow('Mathematics', 0.58, SetuTheme.math),
          ],
        ),
      ),
    );
  }

  Widget _buildSubjectRow(String subject, double progress, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                Container(
                  width: 12.w,
                  height: 12.w,
                  decoration: BoxDecoration(
                    color: color,
                    shape: BoxShape.circle,
                  ),
                ),
                SizedBox(width: 10.w),
                Text(
                  subject,
                  style: TextStyle(
                    fontSize: 14.sp,
                    fontWeight: FontWeight.w500,
                    color: SetuTheme.textPrimary,
                  ),
                ),
              ],
            ),
            Text(
              '${(progress * 100).toInt()}%',
              style: TextStyle(
                fontSize: 14.sp,
                fontWeight: FontWeight.w600,
                color: color,
              ),
            ),
          ],
        ),
        SizedBox(height: 8.h),
        ClipRRect(
          borderRadius: BorderRadius.circular(6.r),
          child: LinearProgressIndicator(
            value: progress,
            backgroundColor: SetuTheme.surfaceVariant,
            valueColor: AlwaysStoppedAnimation<Color>(color),
            minHeight: 10.h,
          ),
        ),
      ],
    );
  }

  Widget _buildConceptCard(ConceptMastery concept) {
    return Padding(
      padding: EdgeInsets.symmetric(horizontal: 20.w, vertical: 6.h),
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
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  concept.emoji,
                  style: TextStyle(fontSize: 24.sp),
                ),
                SizedBox(width: 12.w),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        concept.conceptId
                            .replaceAll('_', ' ')
                            .toUpperCase(),
                        style: TextStyle(
                          fontSize: 14.sp,
                          fontWeight: FontWeight.w600,
                          color: SetuTheme.textPrimary,
                        ),
                      ),
                      SizedBox(height: 4.h),
                      Text(
                        '${concept.exposureCount} attempts • ${(concept.correctApplicationRate * 100).toInt()}% accuracy',
                        style: TextStyle(
                          fontSize: 12.sp,
                          color: SetuTheme.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: EdgeInsets.symmetric(
                    horizontal: 12.w,
                    vertical: 6.h,
                  ),
                  decoration: BoxDecoration(
                    color: concept.color.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8.r),
                  ),
                  child: Text(
                    concept.masteryLevel.toUpperCase(),
                    style: TextStyle(
                      fontSize: 11.sp,
                      fontWeight: FontWeight.w700,
                      color: concept.color,
                    ),
                  ),
                ),
              ],
            ),
            if (concept.specificWeaknesses.isNotEmpty) ...[
              SizedBox(height: 12.h),
              Wrap(
                spacing: 8.w,
                children: concept.specificWeaknesses.map((weakness) {
                  return Chip(
                    label: Text(
                      weakness.replaceAll('_', ' '),
                      style: TextStyle(
                        fontSize: 11.sp,
                        color: SetuTheme.warning,
                      ),
                    ),
                    backgroundColor: SetuTheme.warning.withOpacity(0.1),
                    side: BorderSide.none,
                    padding: EdgeInsets.zero,
                  );
                }).toList(),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildWeakAreasSection() {
    final weakConcepts = _concepts
        .where((c) => c.masteryLevel == 'weak')
        .toList();

    if (weakConcepts.isEmpty) return const SizedBox.shrink();

    return Padding(
      padding: EdgeInsets.all(20.w),
      child: Container(
        padding: EdgeInsets.all(20.w),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              SetuTheme.warning.withOpacity(0.1),
              SetuTheme.warning.withOpacity(0.05),
            ],
          ),
          borderRadius: BorderRadius.circular(20.r),
          border: Border.all(
            color: SetuTheme.warning.withOpacity(0.3),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.trending_up,
                  color: SetuTheme.warning,
                  size: 24.sp,
                ),
                SizedBox(width: 12.w),
                Text(
                  'Focus Areas',
                  style: TextStyle(
                    fontSize: 16.sp,
                    fontWeight: FontWeight.w600,
                    color: SetuTheme.textPrimary,
                  ),
                ),
              ],
            ),
            SizedBox(height: 12.h),
            Text(
              'These concepts need more practice. Setu will prioritize them in your daily tasks.',
              style: TextStyle(
                fontSize: 13.sp,
                color: SetuTheme.textSecondary,
              ),
            ),
            SizedBox(height: 16.h),
            ...weakConcepts.map((concept) {
              return Padding(
                padding: EdgeInsets.only(bottom: 8.h),
                child: Row(
                  children: [
                    Icon(
                      Icons.circle,
                      size: 8.sp,
                      color: SetuTheme.warning,
                    ),
                    SizedBox(width: 10.w),
                    Text(
                      concept.conceptId.replaceAll('_', ' '),
                      style: TextStyle(
                        fontSize: 14.sp,
                        color: SetuTheme.textPrimary,
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }
}
