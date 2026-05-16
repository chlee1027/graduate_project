import React, { useState, useEffect } from "react";
import { View, Text, TextInput, TouchableOpacity, ScrollView, Alert, Modal, FlatList } from "react-native";
import Animated, { useSharedValue, useAnimatedStyle, withSpring, withSequence, withTiming } from "react-native-reanimated";
import { useRouter, Stack } from "expo-router";
import { useUserStore } from "../src/store/userStore";
import client from "../src/api/client";
import { SafeAreaView } from "react-native-safe-area-context";

export default function Onboarding() {
  const router = useRouter();
  const { setUserId, setIsOnboarded } = useUserStore();

  const [isAgeModalVisible, setIsAgeModalVisible] = useState(false);
  const [isHeightModalVisible, setIsHeightModalVisible] = useState(false);
  const [isWeightModalVisible, setIsWeightModalVisible] = useState(false);

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
  });

  // Liquid Animation Logic
  const translateX = useSharedValue((3 - 1) * 40);
  const scaleX = useSharedValue(1);

  useEffect(() => {
    // Even smoother transition with higher damping and lower stiffness to eliminate any oscillation
    translateX.value = withSpring((form.weekly_available_days - 1) * 40, {
      damping: 30,
      stiffness: 100,
    });
    
    // Very subtle stretch effect for a premium, calm feel
    scaleX.value = withSequence(
      withTiming(1.05, { duration: 150 }),
      withSpring(1, { damping: 30 })
    );
  }, [form.weekly_available_days]);

  const animatedBlobStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: translateX.value },
      { scaleX: scaleX.value }
    ],
  }));

  const handleOnboarding = async () => {
    try {
      // Calculate age from birth_year (Current year 2026)
      const currentYear = 2026;
      const calculatedAge = currentYear - form.birth_year;
      
      const submissionForm = {
        ...form,
        age: calculatedAge
      };

      const response = await client.post("/api/onboarding/", submissionForm);
      if (response.status === 200) {
        setUserId(form.user_id);
        setIsOnboarded(true);
        Alert.alert("완료", "온보딩이 성공적으로 완료되었습니다!");
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

  const RowItem = ({ label, children }: any) => (
    <View className="flex-row items-center mb-4">
      <Text className="w-24 text-gray-700 font-bold text-sm">{label}</Text>
      <View className="flex-1">{children}</View>
    </View>
  );

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ title: "", headerShown: false }} />
      <ScrollView className="p-8 pt-12">
        <Text className="text-3xl font-extrabold mb-4 text-gray-900">안녕하세요!</Text>
        <Text className="text-gray-400 mb-10 text-sm">저에게 당신이 누군지 알려주세요 🙌</Text>

        <View className="flex-row mb-8 justify-between px-2">
          <TouchableOpacity
            onPress={() => setForm({ ...form, sex: "male" })}
            className={`w-[44%] aspect-square rounded-3xl border-2 items-center justify-center ${
              form.sex === "male" ? "bg-blue-50 border-blue-600" : "bg-white border-gray-100"
            }`}
          >
            <Text className="text-4xl mb-2">👦</Text>
            <Text className={`text-base font-black ${form.sex === "male" ? "text-blue-600" : "text-gray-400"}`}>남성</Text>
            {form.sex === "male" && (
              <View className="absolute top-2 right-2 w-5 h-5 bg-blue-600 rounded-full items-center justify-center">
                <Text className="text-white text-[10px]">✓</Text>
              </View>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            onPress={() => setForm({ ...form, sex: "female" })}
            className={`w-[44%] aspect-square rounded-3xl border-2 items-center justify-center ${
              form.sex === "female" ? "bg-blue-50 border-blue-600" : "bg-white border-gray-100"
            }`}
          >
            <Text className="text-4xl mb-2">👧</Text>
            <Text className={`text-base font-black ${form.sex === "female" ? "text-blue-600" : "text-gray-400"}`}>여성</Text>
            {form.sex === "female" && (
              <View className="absolute top-2 right-2 w-5 h-5 bg-blue-600 rounded-full items-center justify-center">
                <Text className="text-white text-[10px]">✓</Text>
              </View>
            )}
          </TouchableOpacity>
        </View>

        <RowItem label="출생연도는">
          <TouchableOpacity
            onPress={() => setIsAgeModalVisible(true)}
            className="bg-gray-100 h-12 rounded-full flex-row justify-center items-center"
          >
            <Text className="text-gray-800 font-bold">{form.birth_year}년</Text>
          </TouchableOpacity>
        </RowItem>

        <RowItem label="키는">
          <TouchableOpacity
            onPress={() => setIsHeightModalVisible(true)}
            className="bg-gray-100 h-12 rounded-full flex-row justify-center items-center"
          >
            <Text className="text-gray-800 font-bold">{form.height_cm}cm</Text>
          </TouchableOpacity>
        </RowItem>

        <RowItem label="몸무게는">
          <TouchableOpacity
            onPress={() => setIsWeightModalVisible(true)}
            className="bg-gray-100 h-12 rounded-full flex-row justify-center items-center"
          >
            <Text className="text-gray-800 font-bold">{form.weight_kg}kg</Text>
          </TouchableOpacity>
        </RowItem>

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
        
        <RowItem label="운동 목표는">
          <View className="flex-row">
            {[
              { label: "체중 감량", value: "weight_loss" },
              { label: "근력 증진", value: "muscle_gain" },
              { label: "건강 유지", value: "fitness" },
            ].map((opt) => (
              <TouchableOpacity
                key={opt.value}
                onPress={() => setForm({ ...form, goal: opt.value })}
                className={`flex-1 mr-2 py-3 rounded-full border items-center ${
                  form.goal === opt.value ? "bg-blue-600 border-blue-600" : "bg-white border-gray-300"
                }`}
              >
                <Text className={form.goal === opt.value ? "text-white font-bold text-[11px]" : "text-gray-400 text-[11px] font-bold"}>
                  {opt.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </RowItem>

        <RowItem label="숙련도는">
          <View className="flex-row">
            {[
              { label: "초보", value: "beginner" },
              { label: "중급", value: "intermediate" },
              { label: "상급", value: "advanced" },
            ].map((opt) => (
              <TouchableOpacity
                key={opt.value}
                onPress={() => setForm({ ...form, experience_level: opt.value })}
                className={`flex-1 mr-2 py-3 rounded-full border items-center ${
                  form.experience_level === opt.value ? "bg-blue-600 border-blue-600" : "bg-white border-gray-300"
                }`}
              >
                <Text className={form.experience_level === opt.value ? "text-white font-bold text-[11px]" : "text-gray-400 font-bold text-[11px]"}>
                  {opt.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </RowItem>

        <RowItem label="선호 장소">
          <View className="flex-row">
            <TouchableOpacity
              onPress={() => setForm({ ...form, place_preference: "home" })}
              className={`flex-1 mr-2 py-3 rounded-full border items-center ${
                form.place_preference === "home" ? "bg-blue-600 border-blue-600" : "bg-white border-gray-300"
              }`}
            >
              <Text className={form.place_preference === "home" ? "text-white font-bold text-[11px]" : "text-gray-400 font-bold text-[11px]"}>홈트</Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => setForm({ ...form, place_preference: "gym" })}
              className={`flex-1 py-3 rounded-full border items-center ${
                form.place_preference === "gym" ? "bg-blue-600 border-blue-600" : "bg-white border-gray-300"
              }`}
            >
              <Text className={form.place_preference === "gym" ? "text-white font-bold text-[11px]" : "text-gray-400 font-bold text-[11px]"}>헬스장</Text>
            </TouchableOpacity>
          </View>
        </RowItem>

        <RowItem label="주당 횟수">
          <View className="bg-gray-100 p-1 rounded-2xl flex-row relative h-12 w-[288px] self-start items-center">
            {/* Liquid Background Blob */}
            <Animated.View 
              style={[
                { width: 40, height: 40 },
                animatedBlobStyle
              ]}
              className="bg-blue-600 rounded-xl absolute top-1 left-1 shadow-sm"
            />
            
            {[1, 2, 3, 4, 5, 6, 7].map((day) => (
              <TouchableOpacity
                key={day}
                onPress={() => setForm({ ...form, weekly_available_days: day })}
                className="w-10 h-10 items-center justify-center z-10"
                activeOpacity={0.7}
              >
                <Text className={`font-black text-sm ${form.weekly_available_days === day ? "text-white" : "text-gray-400"}`}>
                  {day}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          <Text className="text-[10px] text-gray-400 mt-2 ml-1">주 {form.weekly_available_days}회 운동을 목표로 합니다.</Text>
        </RowItem>

      </ScrollView>
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
