import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:intl/intl.dart';

import '../models/task_model.dart';
import '../services/offline_storage_service.dart';
import '../utils/theme.dart';
import '../widgets/task_card.dart';

/// Daily Brief Screen - The core "Morning Calm" feature
/// Shows prioritized tasks for the day in three buckets:
/// - Must Do (non-negotiable)
/// - Queued (acknowledged but not worrying)
/// - Done (completed)
class DailyBriefScreen extends StatefulWidget {
  const DailyBriefScreen({super.key});

  @override
  State<DailyBriefScreen> createState() => _DailyBriefScreenState();
}

class _DailyBriefScreenState extends State<DailyBriefScreen> {
  DailyBrief? _brief;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadBrief();
  }

  Future<void> _loadBrief() async {
    final profile = OfflineStorageService.getProfile();
    if (profile != null) {
      // Try to get from local storage first
      final cached = OfflineStorageService.getBriefForDate(
        profile.id, 
        DateTime.now()
      );
      
      if (cached != null) {
        setState(() {
          _brief = cached;
          _isLoading = false;
        });
      } else {
        // Generate mock brief for demo
        await _generateMockBrief(profile.id);
      }
    }
  }

  Future<void> _generateMockBrief(String studentId) async {
    // Mock data for demonstration
    final mockBrief = DailyBrief(
      date: DateTime.now(),
      studentId: studentId,
      energyLevel: 'medium',
      focusSubject: 'Physics',
      mustDo: [
        Task(
          id: 'task_1',
          studentId: studentId,
          title: 'Fix: Torque Sign Convention',
          description: 'You keep mixing these up. 15-minute focused practice.',
          contentType: 'micro_lesson',
          scheduledDate: DateTime.now(),
          estimatedDurationMinutes: 15,
          priority: 'high',
          conceptsTargeted: ['Torque'],
          reason: 'Error pattern detected: sign_convention',
        ),
        Task(
          id: 'task_2',
          studentId: studentId,
          title: 'School HW: NCERT Page 48 Q5-10',
          description: 'Due tomorrow. Uses same sign rules.',
          contentType: 'school_homework',
          scheduledDate: DateTime.now(),
          estimatedDurationMinutes: 45,
          deadline: DateTime.now().add(const Duration(days: 1)),
          priority: 'high',
          conceptsTargeted: ['Rotational Motion'],
          reason: 'School deadline',
        ),
        Task(
          id: 'task_3',
          studentId: studentId,
          title: 'PW Class: Rotational Dynamics',
          description: '4:00 PM | Don\'t miss | New topic: Angular Momentum',
          contentType: 'dpp',
          scheduledDate: DateTime.now(),
          estimatedDurationMinutes: 90,
          priority: 'high',
          conceptsTargeted: ['Angular Momentum'],
          reason: 'Live class - non-negotiable',
        ),
      ],
      queued: [
        Task(
          id: 'task_4',
          studentId: studentId,
          title: 'DPP 13: Questions 1-5',
          description: 'Your error pattern shows fatigue after 5 questions',
          contentType: 'dpp',
          scheduledDate: DateTime.now(),
          estimatedDurationMinutes: 25,
          priority: 'medium',
          conceptsTargeted: ['Torque'],
          reason: 'Quality > quantity',
        ),
        Task(
          id: 'task_5',
          studentId: studentId,
          title: 'Module: Read Page 45-50',
          description: 'Highlight formulas only. No solving.',
          contentType: 'module',
          scheduledDate: DateTime.now(),
          estimatedDurationMinutes: 15,
          priority: 'low',
          conceptsTargeted: ['Moment of Inertia'],
          reason: 'Exposure only',
        ),
      ],
      done: [],
      overallProgress: {
        'Physics': 0.62,
        'Chemistry': 0.75,
        'Math': 0.58,
      },
      weakAreasToday: ['Torque', 'Sign Convention'],
      streakDays: 12,
      stressAlert: null,
      deadlineWarnings: ['School HW due TOMORROW'],
    );

    await OfflineStorageService.saveBrief(mockBrief);
    
    setState(() {
      _brief = mockBrief;
      _isLoading = false;
    });
  }

  Future<void> _completeTask(Task task) async {
    // Show completion dialog
    final result = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (context) => TaskCompleteDialog(task: task),
    );

    if (result != null) {
      // Update task
      await OfflineStorageService.updateTaskStatus(
        task.id,
        'completed',
        score: result['score'],
        errors: result['errors'],
        timeTaken: result['timeTaken'],
      );

      // Reload brief
      await _loadBrief();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Great job! Task completed 🎉'),
            backgroundColor: SetuTheme.success,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12.r),
            ),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SetuTheme.background,
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : CustomScrollView(
              slivers: [
                // App Bar
                SliverToBoxAdapter(
                  child: _buildHeader(),
                ),

                // Stress Alert (if any)
                if (_brief?.stressAlert != null)
                  SliverToBoxAdapter(
                    child: _buildStressAlert(),
                  ),

                // Progress Summary
                SliverToBoxAdapter(
                  child: _buildProgressSummary(),
                ),

                // Must Do Section
                SliverToBoxAdapter(
                  child: _buildSectionHeader(
                    'Must Do Today',
                    _brief?.mustDo.length ?? 0,
                    SetuTheme.priorityHigh,
                  ),
                ),
                SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, index) {
                      final task = _brief!.mustDo[index];
                      return TaskCard(
                        task: task,
                        onComplete: () => _completeTask(task),
                      );
                    },
                    childCount: _brief?.mustDo.length ?? 0,
                  ),
                ),

                // Queued Section
                SliverToBoxAdapter(
                  child: _buildSectionHeader(
                    'Queued for Later',
                    _brief?.queued.length ?? 0,
                    SetuTheme.priorityMedium,
                  ),
                ),
                SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, index) {
                      final task = _brief!.queued[index];
                      return TaskCard(
                        task: task,
                        onComplete: () => _completeTask(task),
                        isDimmed: true,
                      );
                    },
                    childCount: _brief?.queued.length ?? 0,
                  ),
                ),

                // Bottom padding
                SliverToBoxAdapter(
                  child: SizedBox(height: 100.h),
                ),
              ],
            ),
    );
  }

  Widget _buildHeader() {
    final now = DateTime.now();
    final dateFormat = DateFormat('EEEE, MMMM d');

    return Container(
      padding: EdgeInsets.fromLTRB(20.w, 60.h, 20.w, 24.h),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            SetuTheme.primary,
            SetuTheme.primaryDark,
          ],
        ),
        borderRadius: BorderRadius.only(
          bottomLeft: Radius.circular(24.r),
          bottomRight: Radius.circular(24.r),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Date and Energy
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    dateFormat.format(now),
                    style: TextStyle(
                      fontSize: 14.sp,
                      color: SetuTheme.textInverse.withOpacity(0.8),
                    ),
                  ),
                  SizedBox(height: 4.h),
                  Text(
                    'Good Morning, Aarav!',
                    style: TextStyle(
                      fontSize: 24.sp,
                      fontWeight: FontWeight.bold,
                      color: SetuTheme.textInverse,
                    ),
                  ),
                ],
              ),
              Container(
                padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 8.h),
                decoration: BoxDecoration(
                  color: SetuTheme.textInverse.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12.r),
                ),
                child: Row(
                  children: [
                    Text(
                      _brief?.energyEmoji ?? '🔋',
                      style: TextStyle(fontSize: 20.sp),
                    ),
                    SizedBox(width: 6.w),
                    Text(
                      (_brief?.energyLevel ?? 'medium').toUpperCase(),
                      style: TextStyle(
                        fontSize: 12.sp,
                        fontWeight: FontWeight.w600,
                        color: SetuTheme.textInverse,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          SizedBox(height: 20.h),

          // Streak
          Row(
            children: [
              Icon(
                Icons.local_fire_department,
                color: SetuTheme.accent,
                size: 24.sp,
              ),
              SizedBox(width: 8.w),
              Text(
                '${_brief?.streakDays ?? 0} day streak!',
                style: TextStyle(
                  fontSize: 14.sp,
                  fontWeight: FontWeight.w600,
                  color: SetuTheme.textInverse,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStressAlert() {
    return Container(
      margin: EdgeInsets.all(16.w),
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        color: SetuTheme.error.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16.r),
        border: Border.all(color: SetuTheme.error.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Icon(
            Icons.warning_rounded,
            color: SetuTheme.error,
            size: 28.sp,
          ),
          SizedBox(width: 12.w),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Take a Breath',
                  style: TextStyle(
                    fontSize: 16.sp,
                    fontWeight: FontWeight.w600,
                    color: SetuTheme.error,
                  ),
                ),
                SizedBox(height: 4.h),
                Text(
                  _brief?.stressAlert ?? '',
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
    );
  }

  Widget _buildProgressSummary() {
    return Container(
      margin: EdgeInsets.all(16.w),
      padding: EdgeInsets.all(20.w),
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
          Text(
            'Your State',
            style: TextStyle(
              fontSize: 16.sp,
              fontWeight: FontWeight.w600,
              color: SetuTheme.textPrimary,
            ),
          ),
          SizedBox(height: 16.h),

          // Progress bars for each subject
          ...(_brief?.overallProgress.entries ?? []).map((entry) {
            return Padding(
              padding: EdgeInsets.only(bottom: 12.h),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        entry.key,
                        style: TextStyle(
                          fontSize: 14.sp,
                          color: SetuTheme.textSecondary,
                        ),
                      ),
                      Text(
                        '${(entry.value * 100).toInt()}%',
                        style: TextStyle(
                          fontSize: 14.sp,
                          fontWeight: FontWeight.w600,
                          color: SetuTheme.primary,
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 6.h),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4.r),
                    child: LinearProgressIndicator(
                      value: entry.value,
                      backgroundColor: SetuTheme.surfaceVariant,
                      valueColor: AlwaysStoppedAnimation<Color>(
                        entry.value < 0.5 
                            ? SetuTheme.warning 
                            : SetuTheme.success,
                      ),
                      minHeight: 8.h,
                    ),
                  ),
                ],
              ),
            );
          }).toList(),

          if (_brief?.weakAreasToday.isNotEmpty ?? false) ...[
            SizedBox(height: 12.h),
            Divider(),
            SizedBox(height: 12.h),
            Row(
              children: [
                Icon(
                  Icons.trending_up,
                  size: 18.sp,
                  color: SetuTheme.warning,
                ),
                SizedBox(width: 8.w),
                Expanded(
                  child: Text(
                    'Working on: ${_brief?.weakAreasToday.join(", ")}',
                    style: TextStyle(
                      fontSize: 13.sp,
                      color: SetuTheme.textSecondary,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title, int count, Color color) {
    return Padding(
      padding: EdgeInsets.fromLTRB(20.w, 24.h, 20.w, 12.h),
      child: Row(
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
            title,
            style: TextStyle(
              fontSize: 16.sp,
              fontWeight: FontWeight.w600,
              color: SetuTheme.textPrimary,
            ),
          ),
          SizedBox(width: 8.w),
          Container(
            padding: EdgeInsets.symmetric(horizontal: 10.w, vertical: 4.h),
            decoration: BoxDecoration(
              color: color.withOpacity(0.15),
              borderRadius: BorderRadius.circular(12.r),
            ),
            child: Text(
              count.toString(),
              style: TextStyle(
                fontSize: 12.sp,
                fontWeight: FontWeight.w600,
                color: color,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Task Completion Dialog
class TaskCompleteDialog extends StatefulWidget {
  final Task task;

  const TaskCompleteDialog({super.key, required this.task});

  @override
  State<TaskCompleteDialog> createState() => _TaskCompleteDialogState();
}

class _TaskCompleteDialogState extends State<TaskCompleteDialog> {
  double? _score;
  final List<String> _errors = [];
  int _timeTaken = 0;
  final _errorController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20.r),
      ),
      child: Padding(
        padding: EdgeInsets.all(20.w),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Complete Task',
              style: TextStyle(
                fontSize: 20.sp,
                fontWeight: FontWeight.bold,
                color: SetuTheme.textPrimary,
              ),
            ),
            SizedBox(height: 8.h),
            Text(
              widget.task.title,
              style: TextStyle(
                fontSize: 14.sp,
                color: SetuTheme.textSecondary,
              ),
            ),
            SizedBox(height: 24.h),

            // Score input
            Text(
              'How did you do?',
              style: TextStyle(
                fontSize: 14.sp,
                fontWeight: FontWeight.w500,
                color: SetuTheme.textPrimary,
              ),
            ),
            SizedBox(height: 12.h),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildScoreOption(0.0, '😞'),
                _buildScoreOption(0.3, '😕'),
                _buildScoreOption(0.5, '😐'),
                _buildScoreOption(0.7, '🙂'),
                _buildScoreOption(1.0, '🤩'),
              ],
            ),

            if (widget.task.contentType == 'dpp') ...[
              SizedBox(height: 20.h),
              Text(
                'Any errors? (optional)',
                style: TextStyle(
                  fontSize: 14.sp,
                  fontWeight: FontWeight.w500,
                  color: SetuTheme.textPrimary,
                ),
              ),
              SizedBox(height: 8.h),
              TextField(
                controller: _errorController,
                decoration: InputDecoration(
                  hintText: 'e.g., Sign convention confusion',
                  suffixIcon: IconButton(
                    icon: const Icon(Icons.add),
                    onPressed: () {
                      if (_errorController.text.isNotEmpty) {
                        setState(() {
                          _errors.add(_errorController.text);
                          _errorController.clear();
                        });
                      }
                    },
                  ),
                ),
              ),
              if (_errors.isNotEmpty) ...[
                SizedBox(height: 8.h),
                Wrap(
                  spacing: 8.w,
                  children: _errors.map((e) => Chip(
                    label: Text(e, style: TextStyle(fontSize: 12.sp)),
                    onDeleted: () {
                      setState(() {
                        _errors.remove(e);
                      });
                    },
                  )).toList(),
                ),
              ],
            ],

            SizedBox(height: 24.h),

            // Actions
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => Navigator.pop(context),
                    child: const Text('Cancel'),
                  ),
                ),
                SizedBox(width: 12.w),
                Expanded(
                  child: ElevatedButton(
                    onPressed: _score != null
                        ? () {
                            Navigator.pop(context, {
                              'score': _score,
                              'errors': _errors,
                              'timeTaken': _timeTaken,
                            });
                          }
                        : null,
                    child: const Text('Complete'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildScoreOption(double score, String emoji) {
    final isSelected = _score == score;
    return GestureDetector(
      onTap: () => setState(() => _score = score),
      child: Container(
        padding: EdgeInsets.all(12.w),
        decoration: BoxDecoration(
          color: isSelected ? SetuTheme.primary.withOpacity(0.2) : null,
          borderRadius: BorderRadius.circular(12.r),
          border: Border.all(
            color: isSelected ? SetuTheme.primary : SetuTheme.surfaceVariant,
            width: 2,
          ),
        ),
        child: Text(
          emoji,
          style: TextStyle(fontSize: 28.sp),
        ),
      ),
    );
  }
}
