import React, { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, ScrollView, Alert } from "react-native";
import { useRouter, Stack } from "expo-router";
import { useUserStore } from "../src/store/userStore";
import client from "../src/api/client";
import { SafeAreaView } from "react-native-safe-area-context";

export default function Onboarding() {
  const router = useRouter();
  const { setUserId, setIsOnboarded } = useUserStore();

  const [form, setForm] = useState({
    user_id: "user_" + Math.random().toString(36).substr(2, 5),
    age: 25,
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

  const handleOnboarding = async () => {
    try {
      const response = await client.post("/api/onboarding/", form);
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

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ title: "회원 정보 입력" }} />
      <ScrollView className="p-4">
        <Text className="text-xl font-bold mb-4">기본 정보를 입력해주세요</Text>
        
        <View className="mb-4">
          <Text className="text-gray-600 mb-1">사용자 ID (자동생성)</Text>
          <TextInput
            className="bg-gray-100 p-3 rounded-lg"
            value={form.user_id}
            editable={false}
          />
        </View>

        <View className="flex-row justify-between mb-4">
          <View className="flex-1 mr-2">
            <Text className="text-gray-600 mb-1">나이</Text>
            <TextInput
              className="bg-gray-100 p-3 rounded-lg"
              keyboardType="numeric"
              value={form.age.toString()}
              onChangeText={(v) => setForm({ ...form, age: parseInt(v) || 0 })}
            />
          </View>
          <View className="flex-1 ml-2">
            <Text className="text-gray-600 mb-1">성별</Text>
            <TextInput
              className="bg-gray-100 p-3 rounded-lg"
              value={form.sex}
              onChangeText={(v) => setForm({ ...form, sex: v })}
            />
          </View>
        </View>

        <View className="mb-4">
          <Text className="text-gray-600 mb-1">목표</Text>
          <TextInput
            className="bg-gray-100 p-3 rounded-lg"
            placeholder="예: muscle_gain, diet, endurance"
            value={form.goal}
            onChangeText={(v) => setForm({ ...form, goal: v })}
          />
        </View>

        <TouchableOpacity
          className="bg-orange-500 p-4 rounded-xl items-center mt-6"
          onPress={handleOnboarding}
        >
          <Text className="text-white font-bold text-lg">시작하기</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}
