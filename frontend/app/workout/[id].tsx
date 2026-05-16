import React, { useState, useEffect, useRef } from "react";
import { View, Text, TouchableOpacity, ScrollView, Alert, Switch, ActivityIndicator } from "react-native";
import { useRouter, Stack, useLocalSearchParams } from "expo-router";
import { useUserStore } from "../../src/store/userStore";
import client from "../../src/api/client";
import { SafeAreaView } from "react-native-safe-area-context";
import Animated, { FadeIn, FadeOut } from "react-native-reanimated";

export default function WorkoutSession() {
  const router = useRouter();
  const { id, recommendation_id } = useLocalSearchParams();
  const { userId } = useUserStore();

  const [loading, setLoading] = useState(true);
  const [recommendation, setRecommendation] = useState<any>(null);
  const [isSessionActive, setIsSessionActive] = useState(true);
  
  // Session State
  const [timeLeft, setTimeLeft] = useState(0); 
  const [totalTargetTime, setTotalTargetTime] = useState(0);
  const [currentSet, setCurrentSet] = useState(0);

  // Feedback State
  const [completed, setCompleted] = useState(true);
  const [rpe, setRpe] = useState(7);
  const [pain, setPain] = useState(false);

  // Fetch Recommendation Details
  useEffect(() => {
    let isMounted = true;
    const fetchDetails = async () => {
      try {
        const response = await client.get(`/api/recommend/${recommendation_id}`);
        if (isMounted) {
          const data = response.data;
          setRecommendation(data);
          const targetSeconds = (data.selected_plan.minutes || 10) * 60;
          setTimeLeft(targetSeconds);
          setTotalTargetTime(targetSeconds);
          setLoading(false);
        }
      } catch (error) {
        console.error(error);
        if (isMounted) {
          Alert.alert("오류", "운동 정보를 불러오는데 실패했습니다.");
          setLoading(false);
        }
      }
    };
    fetchDetails();
    return () => { isMounted = false; };
  }, [recommendation_id]);

  // Robust Timer Logic
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isSessionActive && !loading && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev) => (prev > 0 ? prev - 1 : 0));
      }, 1000);
    }
    return () => { if (interval) clearInterval(interval); };
  }, [isSessionActive, loading, timeLeft > 0]);

  // Auto-finish logic when sets are done
  useEffect(() => {
    if (recommendation && currentSet >= recommendation.selected_plan.sets && isSessionActive) {
      const timeout = setTimeout(() => {
        setIsSessionActive(false);
        Alert.alert("목표 달성!", "오늘의 모든 세트를 완료했습니다. 기록을 저장해주세요!");
      }, 500);
      return () => clearTimeout(timeout);
    }
  }, [currentSet, recommendation, isSessionActive]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
  };

  const isMinTimeMet = () => {
    if (totalTargetTime === 0) return false;
    const timeSpent = totalTargetTime - timeLeft;
    return timeSpent >= 5; // [테스트용] 5초로 일시 단축 (최종 정리 시 원복 필수)
  };

  const handleFinishSession = () => {
    // 1. 만약 최소 수행 시간을 못 채웠다면 즉시 포기 팝업
    if (!isMinTimeMet()) {
      Alert.alert(
        "정말 포기하시겠어요? 😢",
        "아직 운동 시간이 너무 짧아(최소 5초 필요) 기록이 저장되지 않아요. 그래도 그만두시겠어요?",
        [
          { text: "계속하기", style: "cancel" },
          { 
            text: "포기하기", 
            style: "destructive", 
            onPress: () => router.replace("/") 
          },
        ]
      );
      return;
    }

    // 2. 최소 시간을 채웠다면 정상 종료 흐름 (피드백 화면으로 이동)
    setIsSessionActive(false);
  };

  const handleFinishWorkout = async () => {
    try {
      await client.post("/api/log/", {
        recommendation_id,
        user_id: userId,
        plan_id: id,
        completed,
        actual_minutes: Math.max(1, Math.ceil((totalTargetTime - timeLeft) / 60)),
        actual_sets: currentSet,
        rpe,
        pain_occurred: pain,
      });

      const rewardRes = await client.post("/api/reward/", {
        recommendation_id,
        user_id: userId,
        completed,
        rpe,
        pain_occurred: pain,
        streak: null,
      });

      Alert.alert(
        "수고하셨습니다!",
        `운동이 성공적으로 기록되었습니다.\n보상: ${rewardRes.data.reward.toFixed(2)}점`,
        [{ text: "홈으로", onPress: () => router.replace("/") }]
      );
    } catch (error) {
      console.error(error);
      Alert.alert("오류", "기록 저장 중 문제가 발생했습니다.");
    }
  };

  if (loading) {
    return (
      <View className="flex-1 justify-center items-center bg-white">
        <ActivityIndicator size="large" color="#2563eb" />
        <Text className="mt-4 text-gray-500 font-medium">코치가 세션을 준비하고 있습니다...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ headerShown: false }} />
      <ScrollView className="flex-1 p-6" showsVerticalScrollIndicator={false}>
        <View className="mb-8">
          <Text className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-1">
            {isSessionActive ? "Now Training" : "Review Session"}
          </Text>
          <Text className="text-3xl font-black text-gray-900">
            {recommendation?.selected_plan.name}
          </Text>
        </View>

        {isSessionActive ? (
          <Animated.View entering={FadeIn} exiting={FadeOut} className="items-center">
            {/* Timer */}
            <View className="w-64 h-64 rounded-full border-8 border-blue-50 items-center justify-center mb-10 bg-blue-50/30 shadow-sm">
              <Text className="text-5xl font-black text-blue-600 mb-1">{formatTime(timeLeft)}</Text>
              <Text className="text-blue-300 font-bold text-xs uppercase tracking-tighter">Remaining Time</Text>
            </View>

            {/* Set Tracker */}
            <View className="bg-gray-50 w-full p-8 rounded-[40px] mb-10 items-center border border-gray-100">
              <Text className="text-gray-500 font-bold text-sm mb-4">
                {recommendation?.selected_plan.type === "time-based" ? "진행 상황" : "현재 달성도"}
              </Text>
              
              <View className="items-center mb-6">
                <View className="flex-row items-baseline">
                  <Text className="text-5xl font-black text-gray-900">{currentSet}</Text>
                  <Text className="text-xl font-bold text-gray-400 ml-2">/ {recommendation?.selected_plan.sets} 세트</Text>
                </View>
                
                {recommendation?.selected_plan.type === "rep-based" && (
                  <View className="bg-blue-100 px-4 py-1.5 rounded-full mt-3">
                    <Text className="text-blue-600 font-black text-xs">한 세트에 {recommendation?.selected_plan.reps}회</Text>
                  </View>
                )}

                {recommendation?.selected_plan.type === "time-based" && (
                  <View className="bg-green-100 px-4 py-1.5 rounded-full mt-3">
                    <Text className="text-green-600 font-black text-xs">꾸준히 유지해주세요</Text>
                  </View>
                )}
              </View>
              
              <View className="flex-row w-full justify-center space-x-4">
                {(recommendation?.selected_plan.sets > 1) && (
                  <TouchableOpacity
                    onPress={() => setCurrentSet(Math.max(0, currentSet - 1))}
                    className="w-16 h-16 bg-white border border-gray-200 rounded-2xl items-center justify-center shadow-sm"
                  >
                    <Text className="text-2xl text-gray-600">-</Text>
                  </TouchableOpacity>
                )}
                <TouchableOpacity
                  onPress={() => {
                    if (!isMinTimeMet()) {
                      const remaining = Math.ceil((totalTargetTime * 0.3) - (totalTargetTime - timeLeft));
                      Alert.alert("조금만 더!", `최소 수행 시간(30%)까지 약 ${remaining}초 남았습니다. 🔥`);
                      return;
                    }
                    setCurrentSet(currentSet + 1);
                  }}
                  activeOpacity={isMinTimeMet() ? 0.8 : 1}
                  style={{ backgroundColor: isMinTimeMet() ? "#2563eb" : "#d1d5db" }}
                  className={`h-16 rounded-2xl items-center justify-center shadow-md ${recommendation?.selected_plan.sets > 1 ? "flex-1" : "px-10"}`}
                >
                  <Text className="text-white font-black text-lg">
                    {recommendation?.selected_plan.sets > 1 ? "세트 완료 ⚡️" : "운동 종료하기 🏁"}
                  </Text>
                </TouchableOpacity>
              </View>
              
              {!isMinTimeMet() && (
                <Text className="text-gray-400 text-[10px] mt-4 font-bold text-center px-4">
                  ⚠️ 성실한 데이터 축적을 위해{"\n"}권장 시간의 최소 30%는 진행해주셔야 합니다.
                </Text>
              )}
            </View>

            <TouchableOpacity onPress={handleFinishSession} className="py-4 items-center">
              <Text className="text-gray-400 font-bold text-sm underline">오늘 운동 여기까지만 할게요</Text>
            </TouchableOpacity>
          </Animated.View>
        ) : (
          <Animated.View entering={FadeIn} className="space-y-8">
            <Text className="text-xl font-bold text-gray-800 mb-4 text-center">코치에게 오늘의 운동을 알려주세요!</Text>
            <View className="bg-blue-50 p-8 rounded-[40px] border border-blue-100">
              <View className="flex-row justify-between items-center mb-8">
                <Text className="text-blue-900 font-black text-lg">모두 완료했나요?</Text>
                <Switch value={completed} onValueChange={setCompleted} trackColor={{ false: "#d1d5db", true: "#2563eb" }} />
              </View>

              <View className="mb-8">
                <Text className="text-blue-900 font-black text-lg mb-4">운동 강도는 어땠나요?</Text>
                <View className="flex-row justify-between">
                  {[1, 3, 5, 7, 9, 10].map((num) => (
                    <TouchableOpacity
                      key={num}
                      onPress={() => setRpe(num)}
                      className={`w-10 h-10 rounded-xl justify-center items-center ${rpe === num ? "bg-blue-600 shadow-md" : "bg-white border border-blue-100"}`}
                    >
                      <Text className={`font-black ${rpe === num ? "text-white" : "text-blue-600"}`}>{num}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>

              <View className="flex-row justify-between items-center">
                <View className="flex-1">
                  <Text className="text-blue-900 font-black text-lg">통증이 있었나요?</Text>
                  <Text className="text-blue-400 text-xs">부상을 방지하기 위해 꼭 알려주세요.</Text>
                </View>
                <Switch value={pain} onValueChange={setPain} trackColor={{ false: "#d1d5db", true: "#ef4444" }} />
              </View>
            </View>

            <TouchableOpacity className="bg-gray-900 p-6 rounded-[32px] items-center shadow-xl mt-6" onPress={handleFinishWorkout}>
              <Text className="text-white font-black text-xl">운동 기록 저장하기 ✅</Text>
            </TouchableOpacity>
          </Animated.View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
