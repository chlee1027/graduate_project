import React, { useState, useEffect } from "react";
import { View, Text, TouchableOpacity, ScrollView, ActivityIndicator, Alert, Linking } from "react-native";
import { useRouter, Stack } from "expo-router";
import { useUserStore } from "../src/store/userStore";
import client from "../src/api/client";
import { SafeAreaView } from "react-native-safe-area-context";

export default function Recommend() {
  const router = useRouter();
  const { userId } = useUserStore();
  const [loading, setLoading] = useState(true);
  const [recommendation, setRecommendation] = useState<any>(null);
  const [location, setLocation] = useState<"home" | "gym">("gym");
  const [wantStretching, setWantStretching] = useState(false);

  const fetchRecommendation = async (currentLocation: string, stretching: boolean = false) => {
    setLoading(true);
    try {
      const response = await client.post("/api/recommend/", {
        user_id: userId,
        location: currentLocation,
        available_minutes: 60,
        fatigue: 2,
        sleep_hours: 7.0,
        recent_adherence_7d: 0.8,
        streak: null, // Let backend calculate
        avg_rpe_last_7d: 5.0,
        want_stretching: stretching,
      });
      setRecommendation(response.data);
    } catch (error) {
      console.error(error);
      Alert.alert("오류", "추천을 불러오지 못했습니다. 서버 상태나 네트워크를 확인해주세요.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) {
      fetchRecommendation(location, wantStretching);
    } else {
      setLoading(false);
      Alert.alert("오류", "사용자 정보가 없습니다. 온보딩을 먼저 진행해주세요.");
      router.replace("/onboarding");
    }
  }, [userId]);

  const handleLocationChange = (newLoc: "home" | "gym") => {
    setLocation(newLoc);
    fetchRecommendation(newLoc, wantStretching);
  };

  const toggleStretching = () => {
    const nextValue = !wantStretching;
    setWantStretching(nextValue);
    fetchRecommendation(location, nextValue);
  };

  if (loading) {
    return (
      <View className="flex-1 justify-center items-center">
        <ActivityIndicator size="large" color="#2563eb" />
        <Text className="mt-4 text-gray-500">AI가 {location === "home" ? "홈트" : "헬스장"} 맞춤 운동을 찾고 있습니다...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ title: "추천 결과", headerShown: false }} />
      <ScrollView className="p-6 pt-10" showsVerticalScrollIndicator={false}>
        <View className="mb-8">
          <Text className="text-3xl font-black text-gray-900">오늘의 추천</Text>
        </View>

        <View className="flex-row bg-gray-100 p-1.5 rounded-3xl mb-8">
          <TouchableOpacity
            onPress={() => handleLocationChange("home")}
            className={`flex-1 py-3 rounded-2xl items-center ${location === "home" ? "bg-white shadow-md" : ""}`}
          >
            <Text className={`font-bold ${location === "home" ? "text-blue-600" : "text-gray-400"}`}>🏠 홈트</Text>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={() => handleLocationChange("gym")}
            className={`flex-1 py-3 rounded-2xl items-center ${location === "gym" ? "bg-white shadow-md" : ""}`}
          >
            <Text className={`font-bold ${location === "gym" ? "text-blue-600" : "text-gray-400"}`}>🏋️ 헬스장</Text>
          </TouchableOpacity>
        </View>

        {recommendation ? (
          <>
            <View className={`p-8 rounded-[40px] border mb-8 ${wantStretching ? "bg-green-50 border-green-100" : "bg-blue-50 border-blue-100"}`}>
              <View className="flex-row justify-between items-start mb-6">
                <View>
                  <Text className={`text-[10px] font-black uppercase tracking-widest mb-1 ${wantStretching ? "text-green-600" : "text-blue-600"}`}>
                    {wantStretching ? "액티브 레스트" : "오늘의 플랜"}
                  </Text>
                  <Text className={`text-2xl font-black ${wantStretching ? "text-green-900" : "text-blue-900"}`}>
                    {recommendation.selected_plan.name}
                  </Text>
                </View>
                <View className={`px-3 py-1 rounded-full ${wantStretching ? "bg-green-600" : "bg-blue-600"}`}>
                  <Text className="text-white font-bold text-[10px]">{recommendation.selected_plan.intensity.toUpperCase()}</Text>
                </View>
              </View>
              
              <View className="flex-row mb-8">
                <View className="mr-8">
                  <Text className="text-gray-400 text-[10px] font-bold uppercase mb-1">예상 시간</Text>
                  <Text className="text-gray-900 font-black text-lg">{recommendation.selected_plan.minutes}분</Text>
                </View>
                <View>
                  <Text className="text-gray-400 text-[10px] font-bold uppercase mb-1">세트/횟수</Text>
                  <Text className="text-gray-900 font-black text-lg">{recommendation.selected_plan.sets}세트 × {recommendation.selected_plan.reps}회</Text>
                </View>
              </View>

              {recommendation.selected_plan.video_url && (
                <TouchableOpacity
                  onPress={() => Linking.openURL(recommendation.selected_plan.video_url)}
                  className="bg-white/80 py-4 rounded-2xl flex-row items-center justify-center border border-white shadow-sm active:opacity-90"
                >
                  <Text className={`font-black text-sm ${wantStretching ? "text-green-600" : "text-blue-600"}`}>📺 가이드 영상 보기</Text>
                </TouchableOpacity>
              )}
            </View>

            <TouchableOpacity
              className={`p-5 rounded-3xl items-center shadow-lg mb-4 active:opacity-90 ${wantStretching ? "bg-green-600" : "bg-blue-600"}`}
              onPress={() => router.push({
                pathname: `/workout/${recommendation.selected_plan.plan_id}`,
                params: { recommendation_id: recommendation.recommendation_id }
              })}
            >
              <Text className="text-white font-black text-lg">운동 시작하기</Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={toggleStretching}
              className="py-4 items-center"
            >
              <Text className={`font-bold text-sm ${wantStretching ? "text-blue-600" : "text-gray-400"}`}>
                {wantStretching ? "원래 추천 플랜으로 돌아가기" : "오늘은 몸이 좀 무거워요... (스트레칭)"}
              </Text>
            </TouchableOpacity>
          </>
        ) : (
          <View className="p-10 items-center">
            <Text className="text-gray-400">추천 결과가 없습니다.</Text>
          </View>
        )}
        
        <TouchableOpacity
          className="p-4 items-center"
          onPress={() => fetchRecommendation(location, wantStretching)}
        >
          <Text className="text-blue-600">다른 추천 받기</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}
