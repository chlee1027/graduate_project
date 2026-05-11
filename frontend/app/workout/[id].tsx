import React, { useState } from "react";
import { View, Text, TouchableOpacity, ScrollView, Alert, Switch } from "react-native";
import { useRouter, Stack, useLocalSearchParams } from "expo-router";
import { useUserStore } from "../../src/store/userStore";
import client from "../../src/api/client";
import { SafeAreaView } from "react-native-safe-area-context";

export default function WorkoutDetail() {
  const router = useRouter();
  const { id, recommendation_id } = useLocalSearchParams();
  const { userId } = useUserStore();

  const [completed, setCompleted] = useState(true);
  const [rpe, setRpe] = useState(7);
  const [pain, setPain] = useState(false);

  const handleFinish = async () => {
    try {
      // 1. Log the workout
      await client.post("/api/log/", {
        recommendation_id,
        user_id: userId,
        plan_id: id,
        completed,
        actual_minutes: 30,
        rpe,
        pain_occurred: pain,
      });

      // 2. Get the reward and update bandit
      const rewardRes = await client.post("/api/reward/", {
        recommendation_id,
        user_id: userId,
        completed,
        rpe,
        pain_occurred: pain,
        streak: 1, // Simplified for now
      });

      Alert.alert(
        "운동 완료!",
        `보상: ${rewardRes.data.reward.toFixed(2)}점이 적립되었습니다.`,
        [{ text: "확인", onPress: () => router.replace("/") }]
      );
    } catch (error) {
      console.error(error);
      Alert.alert("오류", "데이터 저장 중 문제가 발생했습니다.");
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ title: "운동 기록" }} />
      <ScrollView className="p-4">
        <Text className="text-xl font-bold mb-6">운동을 마치셨나요?</Text>

        <View className="mb-6 bg-gray-50 p-4 rounded-xl">
          <View className="flex-row justify-between items-center mb-4">
            <Text className="text-gray-700 font-bold">완료 여부</Text>
            <Switch value={completed} onValueChange={setCompleted} />
          </View>

          <View className="mb-4">
            <Text className="text-gray-700 font-bold mb-2">오늘 운동의 강도는? (RPE: {rpe})</Text>
            <View className="flex-row justify-between">
              {[1, 3, 5, 7, 9, 10].map((num) => (
                <TouchableOpacity
                  key={num}
                  onPress={() => setRpe(num)}
                  className={`w-10 h-10 rounded-full justify-center items-center ${
                    rpe === num ? "bg-orange-500" : "bg-gray-200"
                  }`}
                >
                  <Text className={rpe === num ? "text-white" : "text-gray-600"}>{num}</Text>
                </TouchableOpacity>
              ))}
            </View>
            <Text className="text-xs text-gray-400 mt-2">1: 아주 쉬움 ~ 10: 최대 강도</Text>
          </View>

          <View className="flex-row justify-between items-center">
            <Text className="text-gray-700 font-bold">통증 발생 여부</Text>
            <Switch value={pain} onValueChange={setPain} trackColor={{ true: "#ef4444" }} />
          </View>
        </View>

        <TouchableOpacity
          className="bg-orange-500 p-4 rounded-xl items-center shadow-sm"
          onPress={handleFinish}
        >
          <Text className="text-white font-bold text-lg">기록 저장하고 종료</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}
