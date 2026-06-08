import React, { useState, useEffect } from "react";
import { View, Text, TouchableOpacity, ScrollView, Alert, Switch, ActivityIndicator, Platform } from "react-native";
import { useRouter, Stack, useLocalSearchParams } from "expo-router";
import { useUserStore } from "../../src/store/userStore";
import client from "../../src/api/client";
import { SafeAreaView } from "react-native-safe-area-context";
import Animated, { FadeIn, FadeOut } from "react-native-reanimated";

type WorkoutPhase = "WORK" | "REST" | "FEEDBACK";

export default function WorkoutSession() {
  const router = useRouter();
  const { id, recommendation_id } = useLocalSearchParams();
  const { userId } = useUserStore();

  const [loading, setLoading] = useState(true);
  const [recommendation, setRecommendation] = useState<any>(null);
  const [phase, setPhase] = useState<WorkoutPhase>("WORK");
  
  // Timers
  const [elapsedSeconds, setElapsedSeconds] = useState(0); 
  const [totalElapsedSeconds, setTotalElapsedSeconds] = useState(0);
  const [restTimeLeft, setRestTimeLeft] = useState(0);
  const [currentSet, setCurrentSet] = useState(1);

  // Feedback State
  const [completed, setCompleted] = useState(true);
  const [rpe, setRpe] = useState(7);
  
  // Pain State
  const [pain, setPain] = useState(false);
  const [selectedPainParts, setSelectedPainParts] = useState<string[]>([]);
  const [painSeverity, setPainSeverity] = useState<"mild" | "severe">("mild");

  const painPartsList = [
    { id: "knee", label: "무릎" },
    { id: "lower_back", label: "허리" },
    { id: "shoulder", label: "어깨" },
    { id: "wrist", label: "손목" },
    { id: "ankle", label: "발목" },
    { id: "neck", label: "목/경추" },
    { id: "hip", label: "골반/고관절" },
  ];

  const togglePainPart = (partId: string) => {
    setSelectedPainParts(prev => 
      prev.includes(partId) ? prev.filter(p => p !== partId) : [...prev, partId]
    );
  };

  // 1. Stopwatch Logic (Work Phase)
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (phase === "WORK" && !loading) {
      interval = setInterval(() => {
        setElapsedSeconds((prev) => prev + 1);
      }, 1000);
    }
    return () => { if (interval) clearInterval(interval); };
  }, [phase, loading]);

  // 2. Rest Timer Logic
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (phase === "REST" && restTimeLeft > 0) {
      interval = setInterval(() => {
        setRestTimeLeft((prev) => {
          const next = prev > 0 ? prev - 1 : 0;
          if (next === 0) {
            startNextSet();
          }
          return next;
        });
      }, 1000);
    }
    return () => { if (interval) clearInterval(interval); };
  }, [phase, restTimeLeft]);

  // Fetch Details
  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const response = await client.get(`/api/recommend/${recommendation_id}`);
        const data = response.data;
        setRecommendation(data);
        setLoading(false);
      } catch (error) {
        console.error(error);
        Alert.alert("오류", "운동 정보를 불러오는데 실패했습니다.");
        setLoading(false);
      }
    };
    fetchDetails();
  }, [recommendation_id]);

  const startNextSet = () => {
    if (currentSet < recommendation.selected_plan.sets) {
      setCurrentSet(currentSet + 1);
      setElapsedSeconds(0);
      setPhase("WORK");
    } else {
      setPhase("FEEDBACK");
    }
  };

  const handleSetComplete = () => {
    // 누적 시간 업데이트
    setTotalElapsedSeconds(prev => prev + elapsedSeconds);

    if (currentSet < recommendation.selected_plan.sets) {
      setRestTimeLeft(recommendation.selected_plan.rest_seconds || 60); 
      setPhase("REST");
    } else {
      setPhase("FEEDBACK");
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
  };

  const handleFinishWorkout = async () => {
    try {
      const actualMinutes = Math.max(1, Math.round(totalElapsedSeconds / 60));
      
      await client.post("/api/log/", {
        recommendation_id,
        user_id: userId,
        plan_id: id,
        completed,
        actual_minutes: actualMinutes,
        actual_sets: currentSet,
        rpe,
        pain_occurred: pain,
        pain_parts: pain ? selectedPainParts : [],
        pain_severity: pain ? painSeverity : null,
      });

      const rewardRes = await client.post("/api/reward/", {
        recommendation_id,
        user_id: userId,
        completed,
        rpe,
        pain_occurred: pain,
        streak: null,
      });

      if (Platform.OS === 'web') {
        window.alert(`수고하셨습니다!\n총 ${formatTime(totalElapsedSeconds)} 동안 운동하셨네요.\n보상: ${rewardRes.data.reward.toFixed(2)}점`);
        router.replace("/");
      } else {
        Alert.alert(
          "수고하셨습니다!",
          `총 ${formatTime(totalElapsedSeconds)} 동안 운동하셨네요.\n보상: ${rewardRes.data.reward.toFixed(2)}점`,
          [{ text: "홈으로", onPress: () => router.replace("/") }]
        );
      }
    } catch (error) {
      console.error(error);
      if (Platform.OS === 'web') {
        window.alert("오류: 기록 저장 중 문제가 발생했습니다.");
      } else {
        Alert.alert("오류", "기록 저장 중 문제가 발생했습니다.");
      }
    }
  };

  if (loading) return (
    <View className="flex-1 justify-center items-center bg-white">
      <ActivityIndicator size="large" color="#2563eb" />
    </View>
  );

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ headerShown: false }} />
      <ScrollView className="flex-1 p-6" showsVerticalScrollIndicator={false}>
        
        <View className="mb-8">
          <Text className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-1">
            {phase === "WORK" ? `SET ${currentSet} IN PROGRESS` : phase === "REST" ? "RESTING" : "SESSION COMPLETE"}
          </Text>
          <Text className="text-3xl font-black text-gray-900">{recommendation.selected_plan.name}</Text>
        </View>

        {phase === "WORK" && (
          <Animated.View key="work-phase" entering={FadeIn} exiting={FadeOut} className="items-center">
            {/* 오늘의 운동 목표 가이드 추가 */}
            <View className="bg-blue-50 w-full p-4 rounded-2xl mb-6 border border-blue-100 items-center">
              <Text className="text-blue-800 font-black text-lg mb-1">🎯 오늘의 목표</Text>
              <Text className="text-blue-600 font-bold">
                {recommendation.selected_plan.sets}세트 × {recommendation.selected_plan.reps}{recommendation.selected_plan.type === "rep-based" ? "회" : "초"}
              </Text>
            </View>

            <View className="w-64 h-64 rounded-full border-8 border-blue-600 items-center justify-center mb-10 bg-white shadow-xl">
              <Text className="text-6xl font-black text-blue-600 mb-1">{formatTime(elapsedSeconds)}</Text>
              <Text className="text-gray-400 font-bold text-xs uppercase">Elapsed Time</Text>
            </View>

            <View className="bg-gray-50 w-full p-8 rounded-[40px] mb-6 items-center border border-gray-100">
              <Text className="text-5xl font-black text-gray-900 mb-2">{currentSet} <Text className="text-xl text-gray-400">/ {recommendation.selected_plan.sets}</Text></Text>
              <Text className="text-gray-500 font-bold text-sm mb-6">현재 세트 진행 중</Text>
              
              <TouchableOpacity
                onPress={handleSetComplete}
                className="w-full bg-blue-600 h-16 rounded-2xl items-center justify-center shadow-lg"
              >
                <Text className="text-white font-black text-lg">
                  {currentSet === recommendation.selected_plan.sets ? "전체 운동 완료 🏁" : "세트 완료 & 휴식 시작 ⚡️"}
                </Text>
              </TouchableOpacity>
            </View>
          </Animated.View>
        )}

        {phase === "REST" && (
          <Animated.View key="rest-phase" entering={FadeIn} exiting={FadeOut} className="items-center">
            <View className="w-64 h-64 rounded-full border-8 border-green-100 items-center justify-center mb-10 bg-green-50 shadow-sm">
              <Text className="text-6xl font-black text-green-600 mb-1">{formatTime(restTimeLeft)}</Text>
              <Text className="text-green-400 font-bold text-xs uppercase">Recovery Phase</Text>
            </View>

            <View className="bg-gray-50 w-full p-8 rounded-[40px] mb-6 items-center border border-gray-100">
              <Text className="text-2xl font-black text-gray-800 mb-2">꿀맛 같은 휴식 시간 🧘</Text>
              <Text className="text-gray-500 font-bold text-sm mb-8 text-center">다음 세트를 위해 호흡을 가다듬으세요</Text>
              
              <TouchableOpacity
                onPress={startNextSet}
                className="w-full bg-green-600 h-16 rounded-2xl items-center justify-center shadow-lg"
              >
                <Text className="text-white font-black text-lg">휴식 건너뛰고 다음 세트 시작 ❯</Text>
              </TouchableOpacity>
            </View>
          </Animated.View>
        )}

        {phase === "FEEDBACK" && (
          <Animated.View key="feedback-phase" entering={FadeIn} className="space-y-6">
            <View className="bg-blue-600 p-8 rounded-[40px] shadow-xl items-center mb-4">
              <Text className="text-white text-4xl mb-2">🏆</Text>
              <Text className="text-white font-black text-2xl text-center">오늘의 운동을 마쳤습니다!</Text>
            </View>

            <View className="bg-gray-50 p-8 rounded-[40px] border border-gray-100">
              <View className="flex-row justify-between items-center mb-8">
                <Text className="text-gray-800 font-black text-lg">전체 완료했나요?</Text>
                <Switch value={completed} onValueChange={setCompleted} trackColor={{ false: "#d1d5db", true: "#2563eb" }} />
              </View>

              <View className="mb-8">
                <Text className="text-gray-800 font-black text-lg mb-4">운동 강도는 어땠나요?</Text>
                <View className="flex-row justify-between">
                  {[1, 3, 5, 7, 9, 10].map((num) => (
                    <TouchableOpacity
                      key={num}
                      onPress={() => setRpe(num)}
                      className={`w-10 h-10 rounded-xl justify-center items-center ${rpe === num ? "bg-blue-600 shadow-md" : "bg-white border border-gray-100"}`}
                    >
                      <Text className={`font-black ${rpe === num ? "text-white" : "text-blue-600"}`}>{num}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>

              <View className="flex-row justify-between items-center">
                <View className="flex-1">
                  <Text className="text-gray-800 font-black text-lg">통증이 있었나요?</Text>
                  <Text className="text-gray-400 text-xs font-bold">부상을 방지하기 위해 꼭 알려주세요.</Text>
                </View>
                <Switch value={pain} onValueChange={setPain} trackColor={{ false: "#d1d5db", true: "#ef4444" }} />
              </View>

              {pain && (
                <Animated.View entering={FadeIn} className="mt-8 pt-8 border-t border-blue-100">
                  <Text className="text-blue-900 font-black text-base mb-4">어디가 아프신가요? (중복 선택 가능)</Text>
                  <View className="flex-row flex-wrap mb-8">
                    {painPartsList.map((part) => (
                      <TouchableOpacity
                        key={part.id}
                        onPress={() => togglePainPart(part.id)}
                        className={`px-4 py-2.5 rounded-full mr-2 mb-2 border ${
                          selectedPainParts.includes(part.id) 
                            ? "bg-blue-600 border-blue-600" 
                            : "bg-white border-blue-100"
                        }`}
                      >
                        <Text className={`font-bold text-xs ${
                          selectedPainParts.includes(part.id) ? "text-white" : "text-blue-600"
                        }`}>
                          {part.label}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </View>

                  <Text className="text-blue-900 font-black text-base mb-4">통증의 정도는 어떤가요?</Text>
                  <View className="flex-row space-x-3">
                    <TouchableOpacity
                      onPress={() => setPainSeverity("mild")}
                      className={`flex-1 p-4 rounded-2xl border items-center ${
                        painSeverity === "mild" ? "bg-blue-50 border-blue-400" : "bg-white border-gray-100"
                      }`}
                    >
                      <Text className="text-xl mb-1">🧘</Text>
                      <Text className={`font-black text-xs ${painSeverity === "mild" ? "text-blue-700" : "text-gray-400"}`}>약간의 뻐근함</Text>
                      <Text className="text-[8px] text-gray-400 mt-1">7일간 조심하기</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      onPress={() => setPainSeverity("severe")}
                      className={`flex-1 p-4 rounded-2xl border items-center ${
                        painSeverity === "severe" ? "bg-red-50 border-red-400" : "bg-white border-gray-100"
                      }`}
                    >
                      <Text className="text-xl mb-1">🚨</Text>
                      <Text className={`font-black text-xs ${painSeverity === "severe" ? "text-red-700" : "text-gray-400"}`}>심한 통증/부상</Text>
                      <Text className="text-[8px] text-gray-400 mt-1">영구 제외 등록</Text>
                    </TouchableOpacity>
                  </View>
                </Animated.View>
              )}
            </View>

            <TouchableOpacity 
              className="bg-gray-900 p-6 rounded-[32px] items-center shadow-xl mt-4" 
              onPress={handleFinishWorkout}
            >
              <Text className="text-white font-black text-xl">운동 기록 저장하기 ✅</Text>
            </TouchableOpacity>
          </Animated.View>
        )}

        {(phase === "WORK" || phase === "REST") && (
          <TouchableOpacity 
            onPress={() => {
              Alert.alert("운동 중단", "정말 여기서 그만두시겠어요?", [
                { text: "계속하기", style: "cancel" },
                { text: "중단하기", style: "destructive", onPress: () => router.replace("/") }
              ])
            }} 
            className="py-6 items-center"
          >
            <Text className="text-gray-400 font-bold text-sm underline">오늘 운동 여기까지만 할게요</Text>
          </TouchableOpacity>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
