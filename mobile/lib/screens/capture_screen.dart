import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:image_picker/image_picker.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'dart:io';

import '../services/offline_storage_service.dart';
import '../utils/theme.dart';

/// Capture Screen - Post-School Input
/// Students capture what happened in school via:
/// - Photo of blackboard/notes (OCR)
/// - Voice note (transcription)
/// - Quick text input
class CaptureScreen extends StatefulWidget {
  const CaptureScreen({super.key});

  @override
  State<CaptureScreen> createState() => _CaptureScreenState();
}

class _CaptureScreenState extends State<CaptureScreen> {
  final _textController = TextEditingController();
  final _homeworkController = TextEditingController();
  final ImagePicker _picker = ImagePicker();
  final SpeechToText _speech = SpeechToText();
  
  File? _capturedImage;
  bool _isListening = false;
  bool _isProcessing = false;
  String _transcribedText = '';

  @override
  void initState() {
    super.initState();
    _initSpeech();
  }

  Future<void> _initSpeech() async {
    await _speech.initialize();
  }

  Future<void> _capturePhoto() async {
    final XFile? photo = await _picker.pickImage(
      source: ImageSource.camera,
      imageQuality: 85,
    );
    
    if (photo != null) {
      setState(() {
        _capturedImage = File(photo.path);
      });
    }
  }

  Future<void> _pickFromGallery() async {
    final XFile? photo = await _picker.pickImage(
      source: ImageSource.gallery,
      imageQuality: 85,
    );
    
    if (photo != null) {
      setState(() {
        _capturedImage = File(photo.path);
      });
    }
  }

  Future<void> _toggleListening() async {
    if (_isListening) {
      await _speech.stop();
      setState(() => _isListening = false);
    } else {
      if (await _speech.initialize()) {
        setState(() => _isListening = true);
        await _speech.listen(
          onResult: (result) {
            setState(() {
              _transcribedText = result.recognizedWords;
              _textController.text = _transcribedText;
            });
          },
          localeId: 'en_IN', // Indian English
        );
      }
    }
  }

  Future<void> _submitCapture() async {
    if (_textController.text.isEmpty && _capturedImage == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please provide some input')),
      );
      return;
    }

    setState(() => _isProcessing = true);

    // Simulate processing delay
    await Future.delayed(const Duration(seconds: 2));

    // Get student profile
    final profile = OfflineStorageService.getProfile();
    if (profile != null) {
      // In production, this would:
      // 1. OCR the image if present
      // 2. Send to backend for parsing
      // 3. Extract structured data
      // 4. Cross-reference with PW
      
      // For demo, show success
      if (mounted) {
        setState(() => _isProcessing = false);
        
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20.r),
            ),
            title: Row(
              children: [
                Icon(Icons.check_circle, color: SetuTheme.success, size: 28.sp),
                SizedBox(width: 12.w),
                const Text('Captured!'),
              ],
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Topic detected: Rotational Motion',
                  style: TextStyle(
                    fontSize: 14.sp,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                SizedBox(height: 8.h),
                Text(
                  'Homework: Page 48 Q5-10 (due tomorrow)',
                  style: TextStyle(
                    fontSize: 14.sp,
                    color: SetuTheme.textSecondary,
                  ),
                ),
                SizedBox(height: 12.h),
                Container(
                  padding: EdgeInsets.all(12.w),
                  decoration: BoxDecoration(
                    color: SetuTheme.info.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12.r),
                  ),
                  child: Row(
                    children: [
                      Icon(Icons.lightbulb, color: SetuTheme.info, size: 20.sp),
                      SizedBox(width: 8.w),
                      Expanded(
                        child: Text(
                          'PW covered this 3 weeks ago. DPP 08 is perfect warm-up before school numericals.',
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
            ),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.pop(context);
                  Navigator.pop(context);
                },
                child: const Text('Great!'),
              ),
            ],
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SetuTheme.background,
      appBar: AppBar(
        title: const Text('What happened today?'),
        elevation: 0,
      ),
      body: _isProcessing
          ? _buildProcessingView()
          : SingleChildScrollView(
              padding: EdgeInsets.all(20.w),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Welcome message
                  Container(
                    padding: EdgeInsets.all(16.w),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          SetuTheme.primary.withOpacity(0.1),
                          SetuTheme.primary.withOpacity(0.05),
                        ],
                      ),
                      borderRadius: BorderRadius.circular(16.r),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          Icons.school,
                          color: SetuTheme.primary,
                          size: 32.sp,
                        ),
                        SizedBox(width: 16.w),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Welcome back, Aarav!',
                                style: TextStyle(
                                  fontSize: 16.sp,
                                  fontWeight: FontWeight.w600,
                                  color: SetuTheme.textPrimary,
                                ),
                              ),
                              SizedBox(height: 4.h),
                              Text(
                                'School session detected: 8:00 AM - 2:30 PM\nTell Setu what happened today.',
                                style: TextStyle(
                                  fontSize: 13.sp,
                                  color: SetuTheme.textSecondary,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),

                  SizedBox(height: 24.h),

                  // Input methods
                  Text(
                    'How do you want to capture?',
                    style: TextStyle(
                      fontSize: 16.sp,
                      fontWeight: FontWeight.w600,
                      color: SetuTheme.textPrimary,
                    ),
                  ),

                  SizedBox(height: 16.h),

                  // Photo capture
                  _buildCaptureOption(
                    icon: Icons.camera_alt,
                    title: 'Snap blackboard/notes',
                    subtitle: 'OCR will extract text automatically',
                    onTap: _capturePhoto,
                    isActive: _capturedImage != null,
                    trailing: _capturedImage != null
                        ? ClipRRect(
                            borderRadius: BorderRadius.circular(8.r),
                            child: Image.file(
                              _capturedImage!,
                              width: 48.w,
                              height: 48.w,
                              fit: BoxFit.cover,
                            ),
                          )
                        : null,
                  ),

                  SizedBox(height: 12.h),

                  // Voice input
                  _buildCaptureOption(
                    icon: _isListening ? Icons.mic : Icons.mic_none,
                    title: _isListening ? 'Listening...' : 'Tell me (voice)',
                    subtitle: 'Speak in Hindi or English',
                    onTap: _toggleListening,
                    isActive: _isListening,
                    iconColor: _isListening ? SetuTheme.error : null,
                  ),

                  SizedBox(height: 12.h),

                  // Gallery pick
                  _buildCaptureOption(
                    icon: Icons.photo_library,
                    title: 'Pick from gallery',
                    subtitle: 'Select a photo you already took',
                    onTap: _pickFromGallery,
                  ),

                  SizedBox(height: 24.h),

                  // Text input
                  Text(
                    'Or type quickly:',
                    style: TextStyle(
                      fontSize: 14.sp,
                      fontWeight: FontWeight.w500,
                      color: SetuTheme.textSecondary,
                    ),
                  ),

                  SizedBox(height: 12.h),

                  TextField(
                    controller: _textController,
                    maxLines: 4,
                    decoration: InputDecoration(
                      hintText: 'e.g., Today sir taught Rotational Motion. Page 48 ke 5 numericals diye hai...',
                      hintStyle: TextStyle(
                        fontSize: 14.sp,
                        color: SetuTheme.textTertiary,
                      ),
                    ),
                  ),

                  SizedBox(height: 20.h),

                  // Homework section
                  Text(
                    'Homework details (optional):',
                    style: TextStyle(
                      fontSize: 14.sp,
                      fontWeight: FontWeight.w500,
                      color: SetuTheme.textSecondary,
                    ),
                  ),

                  SizedBox(height: 12.h),

                  TextField(
                    controller: _homeworkController,
                    decoration: const InputDecoration(
                      hintText: 'What did sir give? Page numbers, questions, deadline...',
                    ),
                  ),

                  SizedBox(height: 32.h),

                  // Submit button
                  SizedBox(
                    width: double.infinity,
                    height: 56.h,
                    child: ElevatedButton(
                      onPressed: _submitCapture,
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.check_circle_outline),
                          SizedBox(width: 8.w),
                          const Text(
                            'Save & Analyze',
                            style: TextStyle(fontSize: 16),
                          ),
                        ],
                      ),
                    ),
                  ),

                  SizedBox(height: 12.h),

                  Center(
                    child: Text(
                      'Total time: ~3-5 minutes',
                      style: TextStyle(
                        fontSize: 12.sp,
                        color: SetuTheme.textTertiary,
                      ),
                    ),
                  ),

                  SizedBox(height: 40.h),
                ],
              ),
            ),
    );
  }

  Widget _buildProcessingView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          SizedBox(
            width: 80.w,
            height: 80.w,
            child: CircularProgressIndicator(
              strokeWidth: 6,
              valueColor: AlwaysStoppedAnimation<Color>(SetuTheme.primary),
            ),
          ),
          SizedBox(height: 32.h),
          Text(
            'Analyzing your input...',
            style: TextStyle(
              fontSize: 18.sp,
              fontWeight: FontWeight.w600,
              color: SetuTheme.textPrimary,
            ),
          ),
          SizedBox(height: 12.h),
          Text(
            'Extracting topics, formulas, homework\nCross-referencing with PW schedule...',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 14.sp,
              color: SetuTheme.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCaptureOption({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
    bool isActive = false,
    Color? iconColor,
    Widget? trailing,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16.r),
      child: Container(
        padding: EdgeInsets.all(16.w),
        decoration: BoxDecoration(
          color: isActive 
              ? SetuTheme.primary.withOpacity(0.1) 
              : SetuTheme.surface,
          borderRadius: BorderRadius.circular(16.r),
          border: Border.all(
            color: isActive ? SetuTheme.primary : SetuTheme.surfaceVariant,
            width: 2,
          ),
        ),
        child: Row(
          children: [
            Container(
              width: 48.w,
              height: 48.w,
              decoration: BoxDecoration(
                color: (iconColor ?? SetuTheme.primary).withOpacity(0.1),
                borderRadius: BorderRadius.circular(12.r),
              ),
              child: Icon(
                icon,
                color: iconColor ?? SetuTheme.primary,
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
            trailing ?? Icon(
              Icons.arrow_forward_ios,
              size: 16.sp,
              color: SetuTheme.textTertiary,
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _textController.dispose();
    _homeworkController.dispose();
    _speech.stop();
    super.dispose();
  }
}
