"""系统设置 API — 评分权重配置"""
from fastapi import APIRouter, HTTPException
from app.models import ScoringWeights

router = APIRouter()

# 内存存储权重配置
_weights = ScoringWeights()


@router.get("/weights", response_model=ScoringWeights)
async def get_weights():
    """获取评分权重配置"""
    return _weights


@router.put("/weights", response_model=ScoringWeights)
async def save_weights(cfg: ScoringWeights):
    """保存评分权重配置"""
    total = cfg.fundamental + cfg.technical + cfg.capital
    if abs(total - 100) > 0.1:
        raise HTTPException(status_code=400, detail=f"权重总和必须为100（当前{total:.1f}）")
    _weights.fundamental = cfg.fundamental
    _weights.technical = cfg.technical
    _weights.capital = cfg.capital
    return _weights
