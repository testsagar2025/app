import 'package:hive/hive.dart';
import 'package:json_annotation/json_annotation.dart';

part 'task_model.g.dart';

@JsonSerializable()
@HiveType(typeId: 0)
class Task extends HiveObject {
  @HiveField(0)
  final String id;
  
  @HiveField(1)
  final String studentId;
  
  @HiveField(2)
  final String title;
  
  @HiveField(3)
  final String? description;
  
  @HiveField(4)
  final String contentType; // dpp, module, school_homework, revision, micro_lesson
  
  @HiveField(5)
  final String? sourceId;
  
  @HiveField(6)
  final DateTime scheduledDate;
  
  @HiveField(7)
  final int estimatedDurationMinutes;
  
  @HiveField(8)
  final DateTime? deadline;
  
  @HiveField(9)
  final String priority; // high, medium, low, deferred
  
  @HiveField(10)
  String status; // pending, in_progress, completed, skipped
  
  @HiveField(11)
  final List<String> conceptsTargeted;
  
  @HiveField(12)
  final String? reason;
  
  @HiveField(13)
  DateTime? startedAt;
  
  @HiveField(14)
  DateTime? completedAt;
  
  @HiveField(15)
  int? actualDurationMinutes;
  
  @HiveField(16)
  double? score;
  
  @HiveField(17)
  List<String> errorsMade;

  Task({
    required this.id,
    required this.studentId,
    required this.title,
    this.description,
    required this.contentType,
    this.sourceId,
    required this.scheduledDate,
    required this.estimatedDurationMinutes,
    this.deadline,
    required this.priority,
    this.status = 'pending',
    this.conceptsTargeted = const [],
    this.reason,
    this.startedAt,
    this.completedAt,
    this.actualDurationMinutes,
    this.score,
    this.errorsMade = const [],
  });

  factory Task.fromJson(Map<String, dynamic> json) => _$TaskFromJson(json);
  Map<String, dynamic> toJson() => _$TaskToJson(this);

  bool get isOverdue {
    if (deadline == null) return false;
    return deadline!.isBefore(DateTime.now()) && status != 'completed';
  }

  bool get isDueToday {
    if (deadline == null) return false;
    final now = DateTime.now();
    return deadline!.year == now.year && 
           deadline!.month == now.month && 
           deadline!.day == now.day;
  }

  String get durationText {
    if (estimatedDurationMinutes < 60) {
      return '$estimatedDurationMinutes min';
    }
    final hours = estimatedDurationMinutes ~/ 60;
    final mins = estimatedDurationMinutes % 60;
    if (mins == 0) return '$hours hr';
    return '$hours hr $mins min';
  }

  String get iconForType {
    switch (contentType) {
      case 'dpp':
        return '📝';
      case 'module':
        return '📚';
      case 'school_homework':
        return '🏫';
      case 'revision':
        return '🔄';
      case 'micro_lesson':
        return '💡';
      default:
        return '📋';
    }
  }

  Task copyWith({
    String? status,
    DateTime? startedAt,
    DateTime? completedAt,
    int? actualDurationMinutes,
    double? score,
    List<String>? errorsMade,
  }) {
    return Task(
      id: id,
      studentId: studentId,
      title: title,
      description: description,
      contentType: contentType,
      sourceId: sourceId,
      scheduledDate: scheduledDate,
      estimatedDurationMinutes: estimatedDurationMinutes,
      deadline: deadline,
      priority: priority,
      status: status ?? this.status,
      conceptsTargeted: conceptsTargeted,
      reason: reason,
      startedAt: startedAt ?? this.startedAt,
      completedAt: completedAt ?? this.completedAt,
      actualDurationMinutes: actualDurationMinutes ?? this.actualDurationMinutes,
      score: score ?? this.score,
      errorsMade: errorsMade ?? this.errorsMade,
    );
  }
}

@JsonSerializable()
@HiveType(typeId: 1)
class DailyBrief extends HiveObject {
  @HiveField(0)
  final DateTime date;
  
  @HiveField(1)
  final String studentId;
  
  @HiveField(2)
  final String energyLevel; // low, medium, high
  
  @HiveField(3)
  final String? focusSubject;
  
  @HiveField(4)
  final List<Task> mustDo;
  
  @HiveField(5)
  final List<Task> queued;
  
  @HiveField(6)
  final List<Task> done;
  
  @HiveField(7)
  final Map<String, double> overallProgress;
  
  @HiveField(8)
  final List<String> weakAreasToday;
  
  @HiveField(9)
  final int streakDays;
  
  @HiveField(10)
  final String? stressAlert;
  
  @HiveField(11)
  final List<String> deadlineWarnings;

  DailyBrief({
    required this.date,
    required this.studentId,
    required this.energyLevel,
    this.focusSubject,
    this.mustDo = const [],
    this.queued = const [],
    this.done = const [],
    this.overallProgress = const {},
    this.weakAreasToday = const [],
    this.streakDays = 0,
    this.stressAlert,
    this.deadlineWarnings = const [],
  });

  factory DailyBrief.fromJson(Map<String, dynamic> json) => _$DailyBriefFromJson(json);
  Map<String, dynamic> toJson() => _$DailyBriefToJson(this);

  int get totalTasks => mustDo.length + queued.length + done.length;
  int get completedTasks => done.length;
  int get pendingTasks => mustDo.length + queued.length;

  double get completionRate {
    if (totalTasks == 0) return 0;
    return completedTasks / totalTasks;
  }

  String get energyEmoji {
    switch (energyLevel) {
      case 'high':
        return '⚡';
      case 'medium':
        return '🔋';
      case 'low':
        return '🪫';
      default:
        return '🔋';
    }
  }
}

@JsonSerializable()
@HiveType(typeId: 2)
class StudentProfile extends HiveObject {
  @HiveField(0)
  final String id;
  
  @HiveField(1)
  final String name;
  
  @HiveField(2)
  final String grade;
  
  @HiveField(3)
  final String pwBatchCode;
  
  @HiveField(4)
  final List<String> pwSubjects;
  
  @HiveField(5)
  final String? schoolName;
  
  @HiveField(6)
  final String locationType;

  StudentProfile({
    required this.id,
    required this.name,
    required this.grade,
    required this.pwBatchCode,
    required this.pwSubjects,
    this.schoolName,
    this.locationType = 'village',
  });

  factory StudentProfile.fromJson(Map<String, dynamic> json) => _$StudentProfileFromJson(json);
  Map<String, dynamic> toJson() => _$StudentProfileToJson(this);
}

@JsonSerializable()
@HiveType(typeId: 3)
class ConceptMastery extends HiveObject {
  @HiveField(0)
  final String conceptId;
  
  @HiveField(1)
  final int exposureCount;
  
  @HiveField(2)
  final DateTime? firstSeen;
  
  @HiveField(3)
  final DateTime? lastTested;
  
  @HiveField(4)
  final double correctApplicationRate;
  
  @HiveField(5)
  final double confidenceScore;
  
  @HiveField(6)
  final int errorCount;
  
  @HiveField(7)
  final List<String> errorPatterns;
  
  @HiveField(8)
  final List<String> specificWeaknesses;
  
  @HiveField(9)
  final String masteryLevel; // not_started, weak, moderate, strong, mastered
  
  @HiveField(10)
  final DateTime? nextReviewDue;

  ConceptMastery({
    required this.conceptId,
    this.exposureCount = 0,
    this.firstSeen,
    this.lastTested,
    this.correctApplicationRate = 0.0,
    this.confidenceScore = 0.0,
    this.errorCount = 0,
    this.errorPatterns = const [],
    this.specificWeaknesses = const [],
    this.masteryLevel = 'not_started',
    this.nextReviewDue,
  });

  factory ConceptMastery.fromJson(Map<String, dynamic> json) => _$ConceptMasteryFromJson(json);
  Map<String, dynamic> toJson() => _$ConceptMasteryToJson(this);

  String get emoji {
    switch (masteryLevel) {
      case 'mastered':
        return '🏆';
      case 'strong':
        return '💪';
      case 'moderate':
        return '📈';
      case 'weak':
        return '⚠️';
      case 'not_started':
        return '🆕';
      default:
        return '❓';
    }
  }

  Color get color {
    switch (masteryLevel) {
      case 'mastered':
        return const Color(0xFF4CAF50);
      case 'strong':
        return const Color(0xFF8BC34A);
      case 'moderate':
        return const Color(0xFFFFC107);
      case 'weak':
        return const Color(0xFFFF9800);
      case 'not_started':
        return const Color(0xFF9E9E9E);
      default:
        return const Color(0xFF9E9E9E);
    }
  }
}
