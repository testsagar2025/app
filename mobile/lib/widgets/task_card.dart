import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:intl/intl.dart';

import '../models/task_model.dart';
import '../utils/theme.dart';

/// Task Card Widget
/// Displays a task with its priority, duration, and actions
class TaskCard extends StatelessWidget {
  final Task task;
  final VoidCallback? onComplete;
  final VoidCallback? onTap;
  final bool isDimmed;

  const TaskCard({
    super.key,
    required this.task,
    this.onComplete,
    this.onTap,
    this.isDimmed = false,
  });

  Color get _priorityColor {
    switch (task.priority) {
      case 'high':
        return SetuTheme.priorityHigh;
      case 'medium':
        return SetuTheme.priorityMedium;
      case 'low':
        return SetuTheme.priorityLow;
      default:
        return SetuTheme.textTertiary;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Opacity(
      opacity: isDimmed ? 0.7 : 1.0,
      child: Padding(
        padding: EdgeInsets.symmetric(horizontal: 20.w, vertical: 6.h),
        child: Card(
          elevation: isDimmed ? 0 : 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16.r),
            side: isDimmed
                ? BorderSide(color: SetuTheme.surfaceVariant)
                : BorderSide.none,
          ),
          child: InkWell(
            onTap: onTap,
            borderRadius: BorderRadius.circular(16.r),
            child: Padding(
              padding: EdgeInsets.all(16.w),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header row
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Type icon
                      Container(
                        width: 44.w,
                        height: 44.w,
                        decoration: BoxDecoration(
                          color: _getTypeColor().withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12.r),
                        ),
                        child: Center(
                          child: Text(
                            task.iconForType,
                            style: TextStyle(fontSize: 22.sp),
                          ),
                        ),
                      ),
                      SizedBox(width: 14.w),

                      // Title and description
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              task.title,
                              style: TextStyle(
                                fontSize: 15.sp,
                                fontWeight: FontWeight.w600,
                                color: SetuTheme.textPrimary,
                              ),
                            ),
                            if (task.description != null) ...[
                              SizedBox(height: 4.h),
                              Text(
                                task.description!,
                                style: TextStyle(
                                  fontSize: 13.sp,
                                  color: SetuTheme.textSecondary,
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),

                      // Complete button
                      if (onComplete != null)
                        InkWell(
                          onTap: onComplete,
                          borderRadius: BorderRadius.circular(20.r),
                          child: Container(
                            width: 40.w,
                            height: 40.w,
                            decoration: BoxDecoration(
                              color: SetuTheme.success.withOpacity(0.1),
                              shape: BoxShape.circle,
                            ),
                            child: Icon(
                              Icons.check,
                              color: SetuTheme.success,
                              size: 22.sp,
                            ),
                          ),
                        ),
                    ],
                  ),

                  SizedBox(height: 14.h),

                  // Footer row
                  Row(
                    children: [
                      // Duration
                      _buildFooterItem(
                        Icons.schedule,
                        task.durationText,
                        SetuTheme.textSecondary,
                      ),

                      if (task.deadline != null) ...[
                        SizedBox(width: 16.w),
                        _buildFooterItem(
                          Icons.event,
                          _formatDeadline(task.deadline!),
                          task.isOverdue
                              ? SetuTheme.error
                              : task.isDueToday
                                  ? SetuTheme.warning
                                  : SetuTheme.textSecondary,
                        ),
                      ],

                      const Spacer(),

                      // Priority badge
                      Container(
                        padding: EdgeInsets.symmetric(
                          horizontal: 10.w,
                          vertical: 4.h,
                        ),
                        decoration: BoxDecoration(
                          color: _priorityColor.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8.r),
                        ),
                        child: Text(
                          task.priority.toUpperCase(),
                          style: TextStyle(
                            fontSize: 10.sp,
                            fontWeight: FontWeight.w700,
                            color: _priorityColor,
                          ),
                        ),
                      ),
                    ],
                  ),

                  // Reason (if available)
                  if (task.reason != null) ...[
                    SizedBox(height: 12.h),
                    Container(
                      padding: EdgeInsets.all(10.w),
                      decoration: BoxDecoration(
                        color: SetuTheme.info.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(10.r),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            Icons.lightbulb_outline,
                            size: 16.sp,
                            color: SetuTheme.info,
                          ),
                          SizedBox(width: 8.w),
                          Expanded(
                            child: Text(
                              task.reason!,
                              style: TextStyle(
                                fontSize: 12.sp,
                                color: SetuTheme.info,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildFooterItem(IconData icon, String text, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          icon,
          size: 16.sp,
          color: color,
        ),
        SizedBox(width: 6.w),
        Text(
          text,
          style: TextStyle(
            fontSize: 12.sp,
            color: color,
          ),
        ),
      ],
    );
  }

  Color _getTypeColor() {
    switch (task.contentType) {
      case 'dpp':
        return SetuTheme.physics;
      case 'module':
        return SetuTheme.chemistry;
      case 'school_homework':
        return SetuTheme.math;
      case 'revision':
        return SetuTheme.secondary;
      case 'micro_lesson':
        return SetuTheme.accent;
      default:
        return SetuTheme.primary;
    }
  }

  String _formatDeadline(DateTime deadline) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final deadlineDate = DateTime(deadline.year, deadline.month, deadline.day);
    
    final difference = deadlineDate.difference(today).inDays;
    
    if (difference == 0) return 'Today';
    if (difference == 1) return 'Tomorrow';
    if (difference == -1) return 'Yesterday';
    if (difference < 0) return '${-difference} days overdue';
    
    return DateFormat('MMM d').format(deadline);
  }
}

/// Task List Widget
/// Displays a list of tasks
class TaskList extends StatelessWidget {
  final List<Task> tasks;
  final Function(Task)? onTaskComplete;
  final Function(Task)? onTaskTap;
  final String? emptyMessage;

  const TaskList({
    super.key,
    required this.tasks,
    this.onTaskComplete,
    this.onTaskTap,
    this.emptyMessage,
  });

  @override
  Widget build(BuildContext context) {
    if (tasks.isEmpty) {
      return Center(
        child: Padding(
          padding: EdgeInsets.all(40.w),
          child: Column(
            children: [
              Icon(
                Icons.check_circle_outline,
                size: 64.sp,
                color: SetuTheme.textTertiary,
              ),
              SizedBox(height: 16.h),
              Text(
                emptyMessage ?? 'No tasks yet',
                style: TextStyle(
                  fontSize: 16.sp,
                  color: SetuTheme.textSecondary,
                ),
              ),
            ],
          ),
        ),
      );
    }

    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: tasks.length,
      itemBuilder: (context, index) {
        final task = tasks[index];
        return TaskCard(
          task: task,
          onComplete: onTaskComplete != null
              ? () => onTaskComplete!(task)
              : null,
          onTap: onTaskTap != null
              ? () => onTaskTap!(task)
              : null,
        );
      },
    );
  }
}
