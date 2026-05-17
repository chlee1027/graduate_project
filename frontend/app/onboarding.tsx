import React, { useState, useEffect } from "react";
import { View, Text, TextInput, TouchableOpacity, ScrollView, Alert, Modal, FlatList, Platform } from "react-native";
import Animated, { useSharedValue, useAnimatedStyle, withSpring, withSequence, withTiming } from "react-native-reanimated";
import { useRouter, Stack } from "expo-router";
import { useUserStore } from "../src/store/userStore";
import client from "../src/api/client";
import { SafeAreaView } from "react-native-safe-area-context";
import DateTimePicker from "@react-native-community/datetimepicker";

export default function Onboarding() {
  const router = useRouter();
  const { setUserId, setIsOnboarded } = useUserStore();

  const [isAgeModalVisible, setIsAgeModalVisible] = useState(false);
  const [isHeightModalVisible, setIsHeightModalVisible] = useState(false);
  const [isWeightModalVisible, setIsWeightModalVisible] = useState(false);
  const [isTimePickerVisible, setIsTimePickerVisible] = useState(false);

  const [form, setForm] = useState({
    user_id: "user_" + Math.random().toString(36).substr(2, 5),
    birth_year: 1999,
    sex: "male",
    height_cm: 175,
    weight_kg: 70,
    goal: "muscle_gain",
    experience_level: "beginner",
    injuries: [],
    weekly_available_days: 3,
    place_preference: "gym",
    equipment: ["dumbbell", "barbell"],
    workout_time: "08:00", // 기본값 오전 8시
  });

  const [workoutDate, setWorkoutDate] = useState(new Date(2026, 4, 17, 8, 0));

  const onTimeChange = (event: any, selectedDate?: Date) => {
    const show = Platform.OS === 'ios';
    setIsTimePickerVisible(show);
    
    if (selectedDate) {
      setWorkoutDate(selectedDate);
      const hours = selectedDate.getHours().toString().padStart(2, '0');
      const minutes = selectedDate.getMinutes().toString().padStart(2, '0');
      setForm({ ...form, workout_time: `${hours}:${minutes}` });
    }
  };

  // Slider Logic (Dynamic width calculation)
  const [containerWidth, setContainerWidth] = useState(280); // Default safe width
  const segmentWidth = containerWidth / 7;
  const translateX = useSharedValue((3 - 1) * segmentWidth);
  const scaleX = useSharedValue(1);

  useEffect(() => {
    translateX.value = withSpring((form.weekly_available_days - 1) * segmentWidth, {
      damping: 30,
      stiffness: 100,
    });
    
    scaleX.value = withSequence(
      withTiming(1.05, { duration: 150 }),
      withSpring(1, { damping: 30 })
    );
  }, [form.weekly_available_days, segmentWidth]);

  const animatedBlobStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: translateX.value },
      { scaleX: scaleX.value }
    ],
  }));

  const handleOnboarding = async () => {
    try {
      const currentYear = 2026;
      const calculatedAge = currentYear - form.birth_year;
      const submissionForm = { ...form, age: calculatedAge };

      const response = await client.post("/api/onboarding/", submissionForm);
      if (response.status === 200) {
        // 알림 권한 요청 및 운동 알림 예약
        const { registerForPushNotificationsAsync, scheduleWorkoutNotification } = require("../src/services/notificationService");
        await registerForPushNotificationsAsync();
        
        const [hour, minute] = form.workout_time.split(":").map(Number);
        await scheduleWorkoutNotification(hour, minute);

        setUserId(form.user_id);
        setIsOnboarded(true);
        Alert.alert("완료", `온보딩이 성공적으로 완료되었습니다!\n매일 ${form.workout_time}분에 알림을 보내드릴게요. 🔔`);
        router.replace("/");
      }
    } catch (error) {
      console.error(error);
      Alert.alert("오류", "온보딩 중 문제가 발생했습니다.");
    }
  };

  const birthYears = Array.from({ length: 71 }, (_, i) => 2011 - i);
  const heights = Array.from({ length: 81 }, (_, i) => i + 140);
  const weights = Array.from({ length: 111 }, (_, i) => i + 40);
  const hours_morning = ["06", "07", "08", "09", "10", "11"];
  const hours_afternoon = ["12", "13", "14", "15", "16", "17"];
  const hours_evening = ["18", "19", "20", "21", "22", "23"];
  const hours_night = ["00", "01", "02", "03", "04", "05"];
  const minutes = ["00", "15", "30", "45"];

  const TimePickerModal = ({ visible, onClose, selectedTime, onSelect }: any) => {
    const [h, m] = selectedTime.split(":");
    
    const HourGroup = ({ title, data }: { title: string, data: string[] }) => (
      <View className="mb-4">
        <Text className="text-[10px] font-bold text-gray-400 uppercase mb-2 ml-1">{title}</Text>
        <View className="flex-row flex-wrap">
          {data.map((item) => (
            <TouchableOpacity 
              key={item} 
              onPress={() => onSelect(`${item}:${m}`)} 
              className={`w-[15%] aspect-square items-center justify-center rounded-xl mr-2 mb-2 ${h === item ? "bg-blue-600" : "bg-gray-50 border border-gray-100"}`}
            >
              <Text className={`font-black text-sm ${h === item ? "text-white" : "text-gray-600"}`}>{item}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
    );

    return (
      <Modal visible={visible} transparent={true} animationType="slide">
        <View className="flex-1 justify-end bg-black/50">
          <View className="bg-white rounded-t-[48px] p-8 h-[75%]">
            <View className="flex-row justify-between items-center mb-8">
              <View>
                <Text className="text-2xl font-black text-gray-900">시간 설정 ⏰</Text>
                <Text className="text-blue-600 font-bold text-xs mt-1">현재 설정: {h}시 {m}분</Text>
              </View>
              <TouchableOpacity onPress={onClose} className="bg-blue-50 px-6 py-3 rounded-2xl">
                <Text className="text-blue-600 font-black">확인</Text>
              </TouchableOpacity>
            </View>

            <ScrollView showsVerticalScrollIndicator={false} className="flex-1">
              {/* Hour Selection Grid */}
              <View className="mb-8">
                <Text className="text-base font-black text-gray-800 mb-4">시 (Hour)</Text>
                <HourGroup title="Morning" data={hours_morning} />
                <HourGroup title="Afternoon" data={hours_afternoon} />
                <HourGroup title="Evening" data={hours_evening} />
                <HourGroup title="Late Night" data={hours_night} />
              </View>

              {/* Minute Selection Grid */}
              <View className="mb-10">
                <Text className="text-base font-black text-gray-800 mb-4">분 (Minute)</Text>
                <View className="flex-row">
                  {minutes.map((item) => (
                    <TouchableOpacity 
                      key={item} 
                      onPress={() => onSelect(`${h}:${item}`)} 
                      className={`flex-1 aspect-square items-center justify-center rounded-2xl mr-3 ${m === item ? "bg-blue-600" : "bg-gray-50 border border-gray-100"}`}
                    >
                      <Text className={`font-black text-lg ${m === item ? "text-white" : "text-gray-600"}`}>{item}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
            </ScrollView>
          </View>
        </View>
      </Modal>
    );
  };

  const VerticalPickerModal = ({ visible, onClose, data, selectedValue, onSelect, title, unit }: any) => (
    <Modal visible={visible} transparent={true} animationType="slide">
      <View className="flex-1 justify-end bg-black/50">
        <View className="bg-white rounded-t-3xl p-6 h-1/2">
          <View className="flex-row justify-between items-center mb-4">
            <Text className="text-xl font-bold text-gray-800">{title}</Text>
            <TouchableOpacity onPress={onClose}>
              <Text className="text-blue-600 font-bold">완료</Text>
            </TouchableOpacity>
          </View>
          <FlatList
            data={data}
            keyExtractor={(item) => item.toString()}
            renderItem={({ item }) => (
              <TouchableOpacity
                onPress={() => {
                  onSelect(item);
                  onClose();
                }}
                className={`p-4 items-center border-b border-gray-100 ${
                  selectedValue === item ? "bg-blue-50" : ""
                }`}
              >
                <Text className={`text-lg ${selectedValue === item ? "text-blue-600 font-bold" : "text-gray-600"}`}>
                  {item}{unit}
                </Text>
              </TouchableOpacity>
            )}
          />
        </View>
      </View>
    </Modal>
  );

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ title: "", headerShown: false }} />
      <ScrollView className="p-8 pt-6" showsVerticalScrollIndicator={false}>
        <Text className="text-2xl font-black mb-6 text-gray-900 text-center">당신의 정보를 알려주세요 🙌</Text>

        <View className="flex-row mb-6 justify-between px-2">
          <TouchableOpacity
            onPress={() => setForm({ ...form, sex: "male" })}
            className={`w-[47%] aspect-[1.3] rounded-3xl border-2 items-center justify-center ${
              form.sex === "male" ? "bg-blue-50 border-blue-600" : "bg-white border-gray-100"
            }`}
          >
            <Text className="text-3xl mb-1">👦</Text>
            <Text className={`text-sm font-black ${form.sex === "male" ? "text-blue-600" : "text-gray-400"}`}>남성</Text>
            {form.sex === "male" && (
              <View className="absolute top-2 right-2 w-5 h-5 bg-blue-600 rounded-full items-center justify-center">
                <Text className="text-white text-[10px]">✓</Text>
              </View>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            onPress={() => setForm({ ...form, sex: "female" })}
            className={`w-[47%] aspect-[1.3] rounded-3xl border-2 items-center justify-center ${
              form.sex === "female" ? "bg-blue-50 border-blue-600" : "bg-white border-gray-100"
            }`}
          >
            <Text className="text-3xl mb-1">👧</Text>
            <Text className={`text-sm font-black ${form.sex === "female" ? "text-blue-600" : "text-gray-400"}`}>여성</Text>
            {form.sex === "female" && (
              <View className="absolute top-2 right-2 w-5 h-5 bg-blue-600 rounded-full items-center justify-center">
                <Text className="text-white text-[10px]">✓</Text>
              </View>
            )}
          </TouchableOpacity>
        </View>

        {/* Birth Year / Height / Weight Group */}
        <View className="bg-gray-50 p-5 rounded-[32px] mb-6 space-y-3">
          <TouchableOpacity
            onPress={() => setIsAgeModalVisible(true)}
            className="bg-white h-12 rounded-2xl flex-row justify-between items-center px-5 border border-gray-100"
          >
            <Text className="text-gray-400 font-bold text-xs">출생연도</Text>
            <Text className="text-blue-600 font-black text-base">{form.birth_year}년</Text>
          </TouchableOpacity>

          <View className="flex-row justify-between">
            <TouchableOpacity
              onPress={() => setIsHeightModalVisible(true)}
              className="bg-white h-12 rounded-2xl flex-1 flex-row justify-between items-center px-5 mr-3 border border-gray-100"
            >
              <Text className="text-gray-400 font-bold text-[10px]">키</Text>
              <Text className="text-blue-600 font-black text-base">{form.height_cm}cm</Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={() => setIsWeightModalVisible(true)}
              className="bg-white h-12 rounded-2xl flex-1 flex-row justify-between items-center px-5 border border-gray-100"
            >
              <Text className="text-gray-400 font-bold text-[10px]">몸무게</Text>
              <Text className="text-blue-600 font-black text-base">{form.weight_kg}kg</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Rows - Extremely Compact */}
        <View className="space-y-5">
          <View>
            <Text className="text-gray-400 font-bold text-[10px] uppercase tracking-widest mb-2 ml-2">운동 목표</Text>
            <View className="flex-row">
              {[
                { label: "체중 감량", value: "weight_loss" },
                { label: "근력 증진", value: "muscle_gain" },
                { label: "건강 유지", value: "fitness" },
              ].map((opt) => (
                <TouchableOpacity
                  key={opt.value}
                  onPress={() => setForm({ ...form, goal: opt.value })}
                  className={`flex-1 mr-2 py-3 rounded-xl border-2 items-center ${
                    form.goal === opt.value ? "bg-blue-600 border-blue-600 shadow-md" : "bg-white border-gray-100"
                  }`}
                >
                  <Text className={`font-black text-[9px] ${form.goal === opt.value ? "text-white" : "text-gray-400"}`}>
                    {opt.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          <View>
            <Text className="text-gray-400 font-bold text-[10px] uppercase tracking-widest mb-2 ml-2">숙련도</Text>
            <View className="flex-row">
              {[
                { label: "초보", value: "beginner" },
                { label: "중급", value: "intermediate" },
                { label: "상급", value: "advanced" },
              ].map((opt) => (
                <TouchableOpacity
                  key={opt.value}
                  onPress={() => setForm({ ...form, experience_level: opt.value })}
                  className={`flex-1 mr-2 py-3 rounded-xl border-2 items-center ${
                    form.experience_level === opt.value ? "bg-blue-600 border-blue-600 shadow-md" : "bg-white border-gray-100"
                  }`}
                >
                  <Text className={`font-black text-[10px] ${form.experience_level === opt.value ? "text-white" : "text-gray-400"}`}>
                    {opt.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          <View>
            <Text className="text-gray-400 font-bold text-[10px] uppercase tracking-widest mb-2 ml-2">선호 장소</Text>
            <View className="flex-row">
              <TouchableOpacity
                onPress={() => setForm({ ...form, place_preference: "home" })}
                className={`flex-1 mr-2 py-3 rounded-xl border-2 items-center ${
                  form.place_preference === "home" ? "bg-blue-600 border-blue-600 shadow-md" : "bg-white border-gray-100"
                }`}
              >
                <Text className={`font-black text-xs ${form.place_preference === "home" ? "text-white" : "text-gray-400"}`}>🏠 홈트</Text>
              </TouchableOpacity>
              <TouchableOpacity
                onPress={() => setForm({ ...form, place_preference: "gym" })}
                className={`flex-1 py-3 rounded-xl border-2 items-center ${
                  form.place_preference === "gym" ? "bg-blue-600 border-blue-600 shadow-md" : "bg-white border-gray-100"
                }`}
              >
                <Text className={`font-black text-xs ${form.place_preference === "gym" ? "text-white" : "text-gray-400"}`}>🏋️ 헬스장</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>

        {/* Weekly Frequency */}
        <View className="mt-6 mb-10">
          <View className="flex-row justify-between items-center mb-4 ml-2">
            <Text className="text-gray-400 font-bold text-[10px] uppercase tracking-widest">주당 운동 횟수</Text>
            <Text className="text-blue-600 font-black text-base">{form.weekly_available_days}회</Text>
          </View>
          <View 
            className="bg-gray-100 p-1 rounded-xl flex-row relative h-12 self-stretch mx-2 items-center"
            onLayout={(e) => setContainerWidth(e.nativeEvent.layout.width - 8)} // p-1 is 4px * 2 = 8px padding
          >
            <Animated.View 
              style={[
                { width: segmentWidth, height: 40 }, 
                animatedBlobStyle
              ]}
              className="bg-blue-600 rounded-lg absolute top-1 left-1 shadow-sm"
            />
            {[1, 2, 3, 4, 5, 6, 7].map((day) => (
              <TouchableOpacity
                key={day}
                onPress={() => setForm({ ...form, weekly_available_days: day })}
                className="flex-1 items-center justify-center z-10"
              >
                <Text className={`font-black text-sm ${form.weekly_available_days === day ? "text-white" : "text-gray-400"}`}>
                  {day}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Workout Time Picker */}
        <View className="mb-10 px-2">
          <Text className="text-gray-400 font-bold text-[10px] uppercase tracking-widest mb-4 ml-2">운동 알림 시간</Text>
          <TouchableOpacity
            onPress={() => setIsTimePickerVisible(true)}
            className="bg-gray-50 p-6 rounded-[32px] border border-gray-100 flex-row justify-between items-center"
          >
            <View className="flex-row items-center">
              <View className="w-10 h-10 bg-white rounded-2xl items-center justify-center mr-4 shadow-sm">
                <Text className="text-xl">⏰</Text>
              </View>
              <Text className="text-gray-900 font-black text-lg">{form.workout_time}</Text>
            </View>
            <Text className="text-blue-600 font-bold text-xs">변경하기</Text>
          </TouchableOpacity>
        </View>

      </ScrollView>

      {/* 중앙 정렬된 네이티브 시간 선택 모달 */}
      <Modal visible={isTimePickerVisible} transparent={true} animationType="fade">
        <View className="flex-1 justify-center items-center bg-black/50 px-8">
          <View className="bg-white w-full rounded-[40px] p-8 items-center shadow-2xl">
            <Text className="text-xl font-black text-gray-900 mb-6 text-center">언제 운동할까요? ⏰</Text>
            
            <View className="w-full items-center justify-center">
              <DateTimePicker
                value={workoutDate}
                mode="time"
                is24Hour={true}
                display={Platform.OS === 'ios' ? 'spinner' : 'default'}
                onChange={onTimeChange}
                textColor="#111827"
                style={{ width: 250, height: 180 }}
              />
            </View>

            <TouchableOpacity 
              onPress={() => setIsTimePickerVisible(false)}
              className="mt-6 bg-blue-600 w-full py-4 rounded-2xl items-center shadow-lg active:opacity-90"
            >
              <Text className="text-white font-black text-lg">선택 완료</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              onPress={async () => {
                const { testImmediateNotification } = require("../src/services/notificationService");
                await testImmediateNotification();
                Alert.alert("알림 예약", "5초 뒤에 알림이 울리는지 확인해 보세요! 🔔\n(앱을 백그라운드로 내려두시면 더 잘 보입니다)");
              }}
              className="mt-4 bg-gray-100 w-full py-3 rounded-2xl items-center border border-gray-200"
            >
              <Text className="text-gray-500 font-bold">🔔 알림 작동 테스트 (5초 뒤)</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

      <VerticalPickerModal
        visible={isAgeModalVisible}
        onClose={() => setIsAgeModalVisible(false)}
        data={birthYears}
        selectedValue={form.birth_year}
        onSelect={(val: number) => setForm({ ...form, birth_year: val })}
        title="출생연도 선택"
        unit="년"
      />
      <VerticalPickerModal
        visible={isHeightModalVisible}
        onClose={() => setIsHeightModalVisible(false)}
        data={heights}
        selectedValue={form.height_cm}
        onSelect={(val: number) => setForm({ ...form, height_cm: val })}
        title="키 선택"
        unit="cm"
      />
      <VerticalPickerModal
        visible={isWeightModalVisible}
        onClose={() => setIsWeightModalVisible(false)}
        data={weights}
        selectedValue={form.weight_kg}
        onSelect={(val: number) => setForm({ ...form, weight_kg: val })}
        title="몸무게 선택"
        unit="kg"
      />

      <TouchableOpacity
        className="bg-blue-600 p-5 items-center justify-center flex-row"
        onPress={handleOnboarding}
      >
        <Text className="text-white font-bold text-lg mr-2">반가워 👋</Text>
        <Text className="text-white font-bold text-lg">›</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
}
