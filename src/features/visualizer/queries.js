import { useQuery, useMutation } from '@tanstack/react-query';
import { queryKeys } from '../../api/queryKeys.js';
import { UsersRoomsAPI, UsersVisualizeAPI } from '../../api/endpoints.js';

/**
 * Hook to upload room photos (supports base64 or FormData file)
 */
export function useRoomUploadMutation() {
  return useMutation({
    mutationFn: ({ file, base64, filename }) => {
      if (file) {
        return UsersRoomsAPI.uploadFile(file);
      }
      return UsersRoomsAPI.uploadBase64(base64, filename);
    },
  });
}

/**
 * Hook to start an AI visualize compositing job
 */
export function useStartVisualizeMutation() {
  return useMutation({
    mutationFn: (params) => UsersVisualizeAPI.createJob(params),
  });
}

/**
 * Hook to poll an AI visualize job until completed or failed
 */
export function useVisualizeJobQuery(jobId) {
  return useQuery({
    queryKey: queryKeys.visualize.job(jobId),
    queryFn: () => UsersVisualizeAPI.getJob(jobId),
    enabled: !!jobId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data) return 800;
      const status = data.status;
      // Stop polling when reached terminal state
      if (status === 'SUCCESS' || status === 'FAILED' || status === 'ERROR') {
        return false;
      }
      return 800;
    },
  });
}

/**
 * Hook to fetch room details by room ID
 */
export function useRoomQuery(roomId) {
  return useQuery({
    queryKey: queryKeys.rooms.detail(roomId),
    queryFn: () => UsersRoomsAPI.getRoom(roomId),
    enabled: !!roomId,
  });
}
