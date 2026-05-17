import * as Notifications from "expo-notifications";
import * as Device from "expo-device";
import Constants from "expo-constants";
import { Platform } from "react-native";

// 알림 표시 설정 (앱이 켜져 있을 때도 알림을 보여줄지 설정)
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export async function registerForPushNotificationsAsync() {
  let token;

  if (Platform.OS === "android") {
    await Notifications.setNotificationChannelAsync("default", {
      name: "default",
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: "#FF231F7C",
    });
  }

  if (Device.isDevice) {
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    if (existingStatus !== "granted") {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    if (finalStatus !== "granted") {
      console.log("Failed to get push token for push notification!");
      return;
    }
    
    // projectId를 명시적으로 가져오거나 설정
    const projectId = Constants.expoConfig?.extra?.eas?.projectId || Constants.easConfig?.projectId;
    
    try {
      token = (await Notifications.getExpoPushTokenAsync({
        projectId: projectId,
      })).data;
      console.log("Push Token:", token);
    } catch (e) {
      console.log("Error getting push token:", e);
      // 토큰 획득에 실패해도 로컬 알림은 작동할 수 있도록 계속 진행
    }
  } else {
    console.log("Must use physical device for Push Notifications");
  }

  return token;
}

/**
 * 특정 시간에 로컬 알림 예약
 * @param hour 시간 (0-23)
 * @param minute 분 (0-59)
 */
export async function scheduleWorkoutNotification(hour: number, minute: number) {
  // 기존 예약된 알림 모두 취소 (중복 방지)
  await Notifications.cancelAllScheduledNotificationsAsync();

  // 'daily' 타입을 명시적으로 지정하여 매일 반복 예약
  await Notifications.scheduleNotificationAsync({
    content: {
      title: "🏋️ 코치가 기다리고 있어요!",
      body: "오늘의 맞춤 운동이 준비되었습니다. 지금 시작해볼까요?",
      data: { screen: "recommend" },
      sound: true,
    },
    trigger: {
      type: 'daily', // Expo SDK 50+ 명시적 타입
      hour,
      minute,
      channelId: "default",
    } as any,
  });

  console.log(`Daily notification scheduled for ${hour}:${minute}`);
}

/**
 * 5초 후 테스트 알림 발송
 */
export async function testImmediateNotification() {
  await Notifications.scheduleNotificationAsync({
    content: {
      title: "🔔 알림 시스템 확인",
      body: "알림이 정상적으로 작동합니다! 이제 설정하신 시간에 맞춰 코치가 찾아갈게요.",
      sound: true,
    },
    trigger: {
      type: 'timeInterval', // 'timeInterval' 타입을 명시하여 지연 발송 강제
      seconds: 5,
      repeats: false,
      channelId: "default",
    } as any,
  });
}

/**
 * 주간 목표 달성 축하 알림 (즉시 실행 테스트용 등)
 */
export async function sendAchievementNotification() {
  await Notifications.scheduleNotificationAsync({
    content: {
      title: "🎉 주간 목표 달성!",
      body: "이번 주 목표 운동 횟수를 모두 채웠습니다. 대단해요! 🏆",
      sound: true,
    },
    trigger: null, // 즉시 발송
  });
}
