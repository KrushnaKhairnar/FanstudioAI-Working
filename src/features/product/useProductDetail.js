import { useEffect, useMemo } from 'react';
import { useShallow } from 'zustand/react/shallow';
import { useProductQuery, useResolveVariantMutation } from './queries.js';
import { useFinishesQuery } from '../catalog/queries.js';
import { useProductStore } from './store.js';

export function useProductDetail(productId) {
  const {
    data: rawProductData,
    isLoading: isProductLoading,
    error: productError,
  } = useProductQuery(productId);

  const {
    data: rawFinishes = [],
    isLoading: isFinishesLoading,
  } = useFinishesQuery();

  // Select UI options state and actions from useProductStore
  const {
    selectedMotorId,
    setSelectedMotorId,
    selectedBladeId,
    setSelectedBladeId,
    selectedBladeSize,
    setSelectedBladeSize,
    selectedFanType,
    setSelectedFanType,
    selectedColorIdx,
    setSelectedColorIdx,
    selectedThumb,
    setSelectedThumb,
    quantity,
    setQuantity,
  } = useProductStore(
    useShallow((s) => ({
      selectedMotorId: s.selectedMotorId,
      setSelectedMotorId: s.setSelectedMotorId,
      selectedBladeId: s.selectedBladeId,
      setSelectedBladeId: s.setSelectedBladeId,
      selectedBladeSize: s.selectedBladeSize,
      setSelectedBladeSize: s.setSelectedBladeSize,
      selectedFanType: s.selectedFanType,
      setSelectedFanType: s.setSelectedFanType,
      selectedColorIdx: s.selectedColorIdx,
      setSelectedColorIdx: s.setSelectedColorIdx,
      selectedThumb: s.selectedThumb,
      setSelectedThumb: s.setSelectedThumb,
      quantity: s.quantity,
      setQuantity: s.setQuantity,
    }))
  );

  const product = useMemo(() => {
    if (!rawProductData) return null;
    return rawProductData.product || rawProductData;
  }, [rawProductData]);

  const finishes = useMemo(() => {
    let allFinishes = Array.isArray(rawFinishes) ? [...rawFinishes] : [];
    if (rawProductData?.motor_finishes) {
      allFinishes = [
        ...allFinishes.filter((f) => f.type !== 'motor'),
        ...rawProductData.motor_finishes,
      ];
    }
    if (rawProductData?.blade_finishes) {
      allFinishes = [
        ...allFinishes.filter((f) => f.type !== 'blade'),
        ...rawProductData.blade_finishes,
      ];
    }
    return allFinishes;
  }, [rawFinishes, rawProductData]);

  const motorFinishes = useMemo(() => finishes.filter((f) => f.type === 'motor'), [finishes]);
  const bladeFinishes = useMemo(() => finishes.filter((f) => f.type === 'blade'), [finishes]);

  const isLoading = isProductLoading || isFinishesLoading;
  const error = productError?.message || (!isLoading && !product ? 'Product not found' : null);

  // Option Definitions
  const optionDefs = useMemo(() => product?.optionDefinitions || {}, [product]);
  const bladeSizes = useMemo(() => optionDefs.bladeSize || [], [optionDefs]);
  const fanTypes = useMemo(() => optionDefs.fanType || [], [optionDefs]);

  // Set default option selections when product data loads
  useEffect(() => {
    if (bladeSizes.length > 0 && !selectedBladeSize) {
      setSelectedBladeSize(bladeSizes[0]);
    }
    if (fanTypes.length > 0 && !selectedFanType) {
      setSelectedFanType(fanTypes[0]);
    }
  }, [bladeSizes, fanTypes, selectedBladeSize, selectedFanType, setSelectedBladeSize, setSelectedFanType]);

  // Set default finishes when product or finishes load
  useEffect(() => {
    if (!product || finishes.length === 0) return;

    if (!selectedMotorId) {
      if (product.motor_finish_ids && product.motor_finish_ids.length > 0) {
        setSelectedMotorId(product.motor_finish_ids[0]);
      } else {
        const firstMotor = finishes.find((f) => f.type === 'motor');
        if (firstMotor) setSelectedMotorId(firstMotor.finish_id);
      }
    }

    if (!selectedBladeId) {
      if (product.blade_finish_ids && product.blade_finish_ids.length > 0) {
        setSelectedBladeId(product.blade_finish_ids[0]);
      } else {
        const firstBlade = finishes.find((f) => f.type === 'blade');
        if (firstBlade) setSelectedBladeId(firstBlade.finish_id);
      }
    }
  }, [product, finishes, selectedMotorId, selectedBladeId, setSelectedMotorId, setSelectedBladeId]);

  // Resolve Variant Mutation
  const resolveMutation = useResolveVariantMutation();

  useEffect(() => {
    if (!product?.product_id || !selectedMotorId || !selectedBladeId) return;

    resolveMutation.mutate({
      productId: product.product_id,
      motorFinishId: selectedMotorId,
      bladeFinishId: selectedBladeId,
    });
  }, [product?.product_id, selectedMotorId, selectedBladeId]);

  const resolvedVariant = resolveMutation.data?.variant || null;
  const isResolving = resolveMutation.isPending;

  // Calculated price from selected options or base price
  const calculatedPrice = useMemo(() => {
    if (!product) return 0;
    if (product.variants && Array.isArray(product.variants)) {
      const match = product.variants.find(
        (v) =>
          (!selectedBladeSize || v.bladeSize === selectedBladeSize) &&
          (!selectedFanType || v.fanType === selectedFanType)
      );
      if (match && match.mrp) {
        return parseFloat(match.mrp);
      }
    }
    return product.price || product.base_price || 14999;
  }, [product, selectedBladeSize, selectedFanType]);

  return {
    product,
    finishes,
    motorFinishes,
    bladeFinishes,
    isLoading,
    error,
    selectedThumb,
    setSelectedThumb,
    // Options
    bladeSizes,
    fanTypes,
    selectedBladeSize,
    setSelectedBladeSize,
    selectedFanType,
    setSelectedFanType,
    // Finishes
    selectedMotorId,
    setSelectedMotorId,
    selectedBladeId,
    setSelectedBladeId,
    selectedColorIdx,
    setSelectedColorIdx,
    quantity,
    setQuantity,
    // Computed
    calculatedPrice,
    resolvedVariant,
    isResolving,
  };
}
