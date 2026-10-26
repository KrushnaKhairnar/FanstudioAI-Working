import { useEffect, useCallback, useMemo } from 'react';
import { useShallow } from 'zustand/react/shallow';
import { useProductsQuery, useFinishesQuery } from '../catalog/queries.js';
import {
  useRoomUploadMutation,
  useStartVisualizeMutation,
  useVisualizeJobQuery,
} from './queries.js';
import { useVisualizerStore, PRESET_ROOMS } from './store.js';

export function useVisualizer({
  initialProductCode = null,
  initialMotorFinishId = null,
  initialBladeFinishId = null,
} = {}) {
  // Query catalog products & finishes (Server state via TanStack Query)
  const { data: rawProducts = [] } = useProductsQuery();
  const { data: rawFinishes = [] } = useFinishesQuery();

  const products = useMemo(() => (Array.isArray(rawProducts) ? rawProducts : []), [rawProducts]);
  const finishes = useMemo(() => (Array.isArray(rawFinishes) ? rawFinishes : []), [rawFinishes]);

  // Select UI state and actions from useVisualizerStore
  const {
    selectedRoomId,
    roomImage,
    customRooms,
    selectedProductCode,
    selectedMotorId,
    selectedBladeId,
    anchorX,
    anchorY,
    scale,
    rotation,
    downrodLength,
    brightness,
    colorTemp,
    applyShadow,
    applyLighting,
    showComparison,
    compareSplit,
    renderedImageUrl,
    renderTimeMs,
    jobStatus,
    errorMessage,
    activeJobId,
    setSelectedRoom,
    addCustomRoom,
    setSelectedProductCode,
    setSelectedMotorId,
    setSelectedBladeId,
    setAnchor,
    setScale,
    setRotation,
    setDownrodLength,
    setBrightness,
    setColorTemp,
    setApplyShadow,
    setApplyLighting,
    setShowComparison,
    setCompareSplit,
    setRenderedResult,
    setJobStatus,
    setErrorMessage,
    setActiveJobId,
    resetPlacement,
    resetVisualizer,
  } = useVisualizerStore(
    useShallow((s) => ({
      selectedRoomId: s.selectedRoomId,
      roomImage: s.roomImage,
      customRooms: s.customRooms,
      selectedProductCode: s.selectedProductCode,
      selectedMotorId: s.selectedMotorId,
      selectedBladeId: s.selectedBladeId,
      anchorX: s.anchorX,
      anchorY: s.anchorY,
      scale: s.scale,
      rotation: s.rotation,
      downrodLength: s.downrodLength,
      brightness: s.brightness,
      colorTemp: s.colorTemp,
      applyShadow: s.applyShadow,
      applyLighting: s.applyLighting,
      showComparison: s.showComparison,
      compareSplit: s.compareSplit,
      renderedImageUrl: s.renderedImageUrl,
      renderTimeMs: s.renderTimeMs,
      jobStatus: s.jobStatus,
      errorMessage: s.errorMessage,
      activeJobId: s.activeJobId,
      setSelectedRoom: s.setSelectedRoom,
      addCustomRoom: s.addCustomRoom,
      setSelectedProductCode: s.setSelectedProductCode,
      setSelectedMotorId: s.setSelectedMotorId,
      setSelectedBladeId: s.setSelectedBladeId,
      setAnchor: s.setAnchor,
      setScale: s.setScale,
      setRotation: s.setRotation,
      setDownrodLength: s.setDownrodLength,
      setBrightness: s.setBrightness,
      setColorTemp: s.setColorTemp,
      setApplyShadow: s.setApplyShadow,
      setApplyLighting: s.setApplyLighting,
      setShowComparison: s.setShowComparison,
      setCompareSplit: s.setCompareSplit,
      setRenderedResult: s.setRenderedResult,
      setJobStatus: s.setJobStatus,
      setErrorMessage: s.setErrorMessage,
      setActiveJobId: s.setActiveJobId,
      resetPlacement: s.resetPlacement,
      resetVisualizer: s.resetVisualizer,
    }))
  );

  const roomList = useMemo(() => [...customRooms, ...PRESET_ROOMS], [customRooms]);

  // Mutations & Polling Query
  const roomUploadMutation = useRoomUploadMutation();
  const startVisualizeMutation = useStartVisualizeMutation();
  const jobQuery = useVisualizeJobQuery(activeJobId);

  // Initialize store from params or catalog defaults
  useEffect(() => {
    if (initialProductCode && !selectedProductCode) {
      setSelectedProductCode(initialProductCode);
    }
    if (initialMotorFinishId && !selectedMotorId) {
      setSelectedMotorId(initialMotorFinishId);
    }
    if (initialBladeFinishId && !selectedBladeId) {
      setSelectedBladeId(initialBladeFinishId);
    }
  }, [
    initialProductCode,
    initialMotorFinishId,
    initialBladeFinishId,
    selectedProductCode,
    selectedMotorId,
    selectedBladeId,
    setSelectedProductCode,
    setSelectedMotorId,
    setSelectedBladeId,
  ]);

  // Resolve selected product model from products catalog
  const selectedProduct = useMemo(() => {
    if (products.length === 0) return null;
    if (selectedProductCode) {
      const match = products.find(
        (p) =>
          p.product_id === selectedProductCode ||
          p.productId === selectedProductCode ||
          p.product_code === selectedProductCode ||
          p.fanCode === selectedProductCode
      );
      if (match) return match;
    }
    return products[0] || null;
  }, [products, selectedProductCode]);

  // Auto-set selectedProductCode if none set yet
  useEffect(() => {
    if (!selectedProductCode && products.length > 0) {
      const firstId = products[0].product_id || products[0].productId;
      if (firstId) setSelectedProductCode(firstId);
    }
  }, [selectedProductCode, products, setSelectedProductCode]);

  // Default finishes selection when selectedProduct or finishes load
  useEffect(() => {
    if (!selectedProduct) return;

    if (!selectedMotorId) {
      if (initialMotorFinishId) {
        const match = finishes.find(
          (f) =>
            f.type === 'motor' &&
            (f.finish_id === initialMotorFinishId || f.name.toLowerCase() === initialMotorFinishId.toLowerCase())
        );
        if (match) setSelectedMotorId(match.finish_id);
      } else if (selectedProduct.motor_finish_ids?.length > 0) {
        setSelectedMotorId(selectedProduct.motor_finish_ids[0]);
      }
    }

    if (!selectedBladeId) {
      if (initialBladeFinishId) {
        const match = finishes.find(
          (f) =>
            f.type === 'blade' &&
            (f.finish_id === initialBladeFinishId || f.name.toLowerCase() === initialBladeFinishId.toLowerCase())
        );
        if (match) setSelectedBladeId(match.finish_id);
      } else if (selectedProduct.blade_finish_ids?.length > 0) {
        setSelectedBladeId(selectedProduct.blade_finish_ids[0]);
      }
    }
  }, [
    selectedProduct,
    finishes,
    selectedMotorId,
    selectedBladeId,
    initialMotorFinishId,
    initialBladeFinishId,
    setSelectedMotorId,
    setSelectedBladeId,
  ]);

  // Sync polling job query output
  useEffect(() => {
    if (jobQuery.data) {
      if (jobQuery.data.status === 'SUCCESS') {
        setRenderedResult({
          url: jobQuery.data.result_url,
          renderTimeMs: jobQuery.data.render_time_ms,
        });
      } else if (jobQuery.data.status === 'FAILED' || jobQuery.data.status === 'ERROR') {
        setJobStatus('ERROR');
        setErrorMessage(jobQuery.data.error || 'Visualization rendering failed');
        setActiveJobId(null);
      }
    }
  }, [jobQuery.data, setRenderedResult, setJobStatus, setErrorMessage, setActiveJobId]);

  // Handle room upload
  const handleUploadRoom = useCallback(
    async (file) => {
      if (!file) return;
      setErrorMessage(null);

      const reader = new FileReader();
      reader.onload = async () => {
        try {
          const base64Data = reader.result;
          const res = await roomUploadMutation.mutateAsync({
            base64: base64Data,
            filename: file.name,
          });
          if (res && res.image_url) {
            const newRoom = {
              id: res.room_id,
              name: file.name.replace(/\.[^/.]+$/, ''),
              imageUrl: res.image_url,
              ceilingX: res.analysis?.ceiling_center_x ?? 0.50,
              ceilingY: res.analysis?.ceiling_center_y ?? 0.22,
            };
            addCustomRoom(newRoom);
          }
        } catch (err) {
          console.error('Room upload error:', err);
          setErrorMessage(err.message || 'Failed to upload room photo');
        }
      };
      reader.readAsDataURL(file);
    },
    [roomUploadMutation, addCustomRoom, setErrorMessage]
  );

  // Handle AI render job
  const handleRenderAI = useCallback(async () => {
    if (!selectedProduct) return;
    setJobStatus('PROCESSING');
    setErrorMessage(null);

    try {
      const variantId =
        selectedProduct.variant_id ||
        (Array.isArray(selectedProduct.variants) && selectedProduct.variants[0]?.variant_id) ||
        (Array.isArray(selectedProduct.variants) && selectedProduct.variants[0]?.id) ||
        `var-${selectedProduct.product_id}`;

      const payload = {
        product_id: selectedProduct.product_id,
        variant_id: variantId,
        motor_finish_id: selectedMotorId,
        blade_finish_id: selectedBladeId,
        room_image_url: roomImage,
        anchor_x: anchorX,
        anchor_y: anchorY,
        scale_factor: scale,
        rotation_deg: rotation,
        ambient_brightness: brightness,
        color_temp_kelvin: colorTemp,
        apply_shadow: applyShadow,
        apply_lighting: applyLighting,
      };

      const jobRes = await startVisualizeMutation.mutateAsync(payload);

      if (jobRes && jobRes.status === 'SUCCESS' && jobRes.result_url) {
        setRenderedResult({
          url: jobRes.result_url,
          renderTimeMs: jobRes.render_time_ms,
        });
      } else if (jobRes && jobRes.job_id) {
        setActiveJobId(jobRes.job_id);
      } else {
        setJobStatus('SUCCESS');
      }
    } catch (err) {
      console.error('Render error:', err);
      setJobStatus('ERROR');
      setErrorMessage(err.message || 'AI Compositing pipeline error');
    }
  }, [
    selectedProduct,
    selectedMotorId,
    selectedBladeId,
    roomImage,
    anchorX,
    anchorY,
    scale,
    rotation,
    brightness,
    colorTemp,
    applyShadow,
    applyLighting,
    startVisualizeMutation,
    setJobStatus,
    setErrorMessage,
    setRenderedResult,
    setActiveJobId,
  ]);

  return {
    // Server state
    products,
    finishes,
    selectedProduct,
    // Room state & handlers
    roomImage,
    roomList,
    activeRoomId: selectedRoomId,
    isUploadingRoom: roomUploadMutation.isPending,
    handleUploadRoom,
    handleSelectRoom: setSelectedRoom,
    // Selection state
    selectedMotorId,
    setSelectedMotorId,
    selectedBladeId,
    setSelectedBladeId,
    setSelectedProduct: (prod) => setSelectedProductCode(prod?.product_id || prod?.productId || null),
    // Controls
    anchorX,
    setAnchorX: (x) => setAnchor(x, anchorY),
    anchorY,
    setAnchorY: (y) => setAnchor(anchorX, y),
    setAnchor,
    scale,
    setScale,
    rotation,
    setRotation,
    downrodLength,
    setDownrodLength,
    brightness,
    setBrightness,
    colorTemp,
    setColorTemp,
    applyShadow,
    setApplyShadow,
    applyLighting,
    setApplyLighting,
    resetPlacement,
    resetVisualizer,
    // AI Pipeline state
    jobStatus,
    renderedImageUrl,
    renderTimeMs,
    errorMessage,
    handleRenderAI,
    // Comparison
    showComparison,
    setShowComparison,
    compareSplit,
    setCompareSplit,
  };
}
