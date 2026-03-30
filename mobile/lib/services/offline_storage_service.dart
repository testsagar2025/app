import 'package:hive/hive.dart';
import '../models/task_model.dart';

/// Offline-first storage service using Hive
/// All data is stored locally and synced when online
class OfflineStorageService {
  static late Box<Task> _tasksBox;
  static late Box<DailyBrief> _briefsBox;
  static late Box<StudentProfile> _profileBox;
  static late Box<ConceptMastery> _conceptsBox;
  static late Box _syncQueueBox;

  static Future<void> initialize() async {
    // Register adapters
    Hive.registerAdapter(TaskAdapter());
    Hive.registerAdapter(DailyBriefAdapter());
    Hive.registerAdapter(StudentProfileAdapter());
    Hive.registerAdapter(ConceptMasteryAdapter());

    // Open boxes
    _tasksBox = await Hive.openBox<Task>('tasks');
    _briefsBox = await Hive.openBox<DailyBrief>('briefs');
    _profileBox = await Hive.openBox<StudentProfile>('profile');
    _conceptsBox = await Hive.openBox<ConceptMastery>('concepts');
    _syncQueueBox = await Hive.openBox('sync_queue');
  }

  // ==================== Tasks ====================
  
  static Future<void> saveTask(Task task) async {
    await _tasksBox.put(task.id, task);
    await _queueForSync('task', task.id);
  }

  static Future<void> saveTasks(List<Task> tasks) async {
    final Map<String, Task> taskMap = {
      for (var task in tasks) task.id: task
    };
    await _tasksBox.putAll(taskMap);
  }

  static Task? getTask(String id) {
    return _tasksBox.get(id);
  }

  static List<Task> getAllTasks() {
    return _tasksBox.values.toList();
  }

  static List<Task> getTasksForDate(DateTime date) {
    return _tasksBox.values.where((task) {
      return task.scheduledDate.year == date.year &&
             task.scheduledDate.month == date.month &&
             task.scheduledDate.day == date.day;
    }).toList();
  }

  static List<Task> getPendingTasks() {
    return _tasksBox.values
        .where((task) => task.status == 'pending' || task.status == 'in_progress')
        .toList();
  }

  static List<Task> getCompletedTasks() {
    return _tasksBox.values
        .where((task) => task.status == 'completed')
        .toList();
  }

  static Future<void> updateTaskStatus(
    String taskId, 
    String status, {
    double? score,
    List<String>? errors,
    int? timeTaken,
  }) async {
    final task = _tasksBox.get(taskId);
    if (task != null) {
      task.status = status;
      if (score != null) task.score = score;
      if (errors != null) task.errorsMade = errors;
      if (timeTaken != null) task.actualDurationMinutes = timeTaken;
      await task.save();
      await _queueForSync('task_update', taskId);
    }
  }

  static Future<void> deleteTask(String id) async {
    await _tasksBox.delete(id);
  }

  // ==================== Daily Briefs ====================
  
  static Future<void> saveBrief(DailyBrief brief) async {
    final key = '${brief.studentId}_${brief.date.toIso8601String()}';
    await _briefsBox.put(key, brief);
  }

  static DailyBrief? getBriefForDate(String studentId, DateTime date) {
    final key = '${studentId}_${date.toIso8601String()}';
    return _briefsBox.get(key);
  }

  static List<DailyBrief> getAllBriefs(String studentId) {
    return _briefsBox.values
        .where((brief) => brief.studentId == studentId)
        .toList();
  }

  // ==================== Profile ====================
  
  static Future<void> saveProfile(StudentProfile profile) async {
    await _profileBox.put('current', profile);
  }

  static StudentProfile? getProfile() {
    return _profileBox.get('current');
  }

  static Future<void> clearProfile() async {
    await _profileBox.delete('current');
  }

  // ==================== Concepts ====================
  
  static Future<void> saveConcept(ConceptMastery concept) async {
    await _conceptsBox.put(concept.conceptId, concept);
  }

  static Future<void> saveConcepts(List<ConceptMastery> concepts) async {
    final Map<String, ConceptMastery> conceptMap = {
      for (var c in concepts) c.conceptId: c
    };
    await _conceptsBox.putAll(conceptMap);
  }

  static ConceptMastery? getConcept(String conceptId) {
    return _conceptsBox.get(conceptId);
  }

  static List<ConceptMastery> getAllConcepts() {
    return _conceptsBox.values.toList();
  }

  static List<ConceptMastery> getWeakConcepts() {
    return _conceptsBox.values
        .where((c) => c.masteryLevel == 'weak' || c.masteryLevel == 'not_started')
        .toList();
  }

  static List<ConceptMastery> getConceptsForReview() {
    final now = DateTime.now();
    return _conceptsBox.values.where((c) {
      if (c.nextReviewDue == null) return false;
      return c.nextReviewDue!.isBefore(now) || c.nextReviewDue!.isAtSameMomentAs(now);
    }).toList();
  }

  // ==================== Sync Queue ====================
  
  static Future<void> _queueForSync(String type, String id) async {
    final item = {
      'type': type,
      'id': id,
      'timestamp': DateTime.now().toIso8601String(),
    };
    final key = '${type}_$id';
    await _syncQueueBox.put(key, item);
  }

  static List<Map<String, dynamic>> getSyncQueue() {
    return _syncQueueBox.values
        .map((item) => Map<String, dynamic>.from(item as Map))
        .toList();
  }

  static Future<void> removeFromSyncQueue(String type, String id) async {
    final key = '${type}_$id';
    await _syncQueueBox.delete(key);
  }

  static Future<void> clearSyncQueue() async {
    await _syncQueueBox.clear();
  }

  // ==================== Statistics ====================
  
  static Map<String, dynamic> getStatistics() {
    final tasks = getAllTasks();
    final completed = tasks.where((t) => t.status == 'completed').toList();
    
    return {
      'totalTasks': tasks.length,
      'completedTasks': completed.length,
      'completionRate': tasks.isEmpty ? 0 : completed.length / tasks.length,
      'totalStudyMinutes': completed.fold<int>(
        0, 
        (sum, t) => sum + (t.actualDurationMinutes ?? 0)
      ),
      'conceptsMastered': getAllConcepts()
          .where((c) => c.masteryLevel == 'mastered')
          .length,
      'weakAreas': getWeakConcepts().length,
    };
  }

  // ==================== Clear All ====================
  
  static Future<void> clearAll() async {
    await _tasksBox.clear();
    await _briefsBox.clear();
    await _profileBox.clear();
    await _conceptsBox.clear();
    await _syncQueueBox.clear();
  }
}
