from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Form
from typing import List, Optional
import base64

from app.api.schemas.agents import AgentSessionCreate
from app.domain.agents import AgentSession
from app.domain.users import UserInDB
from app.domain.states import AgentState
from app.domain.trajectories import TrajectoryStep
from app.api.dependencies.authentication import get_current_user
from app.api.dependencies.agent import get_agent_session_repository, get_trajectory_repository, get_closed_loop_agent
from app.persistence.mongodb.repositories.agents import AgentSessionRepository
from app.persistence.mongodb.repositories.trajectories import TrajectoryRepository
from app.orchestration.agent import ClosedLoopAgent
from app.state.tracker import StateTracker

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

@router.post("", response_model=AgentSession, status_code=status.HTTP_201_CREATED)
async def create_agent_session(
    request: AgentSessionCreate,
    current_user: UserInDB = Depends(get_current_user),
    agent_repo: AgentSessionRepository = Depends(get_agent_session_repository),
    trajectory_repo: TrajectoryRepository = Depends(get_trajectory_repository)
):
    # 1. Create the session record
    session = await agent_repo.create(
        user_id=current_user.id,
        title=request.title,
        goal=request.goal,
        scenario_id=request.scenario_id
    )
    
    # 2. Initialize the state
    initial_state = StateTracker.initialize_state(
        agent_id=session.agent_session_id,
        goal=session.goal,
        scenario_id=session.scenario_id
    )
    
    # 3. Persist the initial state
    await trajectory_repo.save_latest_state(current_user.id, session.agent_session_id, initial_state)
    
    return session

@router.get("", response_model=List[AgentSession])
async def list_agent_sessions(
    limit: int = 20,
    current_user: UserInDB = Depends(get_current_user),
    agent_repo: AgentSessionRepository = Depends(get_agent_session_repository)
):
    return await agent_repo.list_by_user(current_user.id, limit)

@router.get("/{agent_id}", response_model=AgentSession)
async def get_agent_session(
    agent_id: str,
    current_user: UserInDB = Depends(get_current_user),
    agent_repo: AgentSessionRepository = Depends(get_agent_session_repository)
):
    session = await agent_repo.get_by_id(current_user.id, agent_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent session not found")
    return session

@router.get("/{agent_id}/state", response_model=AgentState)
async def get_agent_state(
    agent_id: str,
    current_user: UserInDB = Depends(get_current_user),
    trajectory_repo: TrajectoryRepository = Depends(get_trajectory_repository)
):
    state = await trajectory_repo.get_latest_state(current_user.id, agent_id)
    if not state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent state not found")
    return state

@router.get("/{agent_id}/trajectory", response_model=List[TrajectoryStep])
async def get_agent_trajectory(
    agent_id: str,
    current_user: UserInDB = Depends(get_current_user),
    trajectory_repo: TrajectoryRepository = Depends(get_trajectory_repository)
):
    trajectory = await trajectory_repo.get_trajectory(current_user.id, agent_id)
    return trajectory

@router.post("/{agent_id}/step", response_model=AgentState)
async def step_agent(
    agent_id: str,
    image: Optional[UploadFile] = File(None),
    observation_ref: Optional[str] = Form(None),
    current_user: UserInDB = Depends(get_current_user),
    agent_repo: AgentSessionRepository = Depends(get_agent_session_repository),
    agent: ClosedLoopAgent = Depends(get_closed_loop_agent)
):
    session = await agent_repo.get_by_id(current_user.id, agent_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent session not found")
        
    image_bytes = None
    if image:
        image_bytes = await image.read()
        
    try:
        new_state = await agent.step(
            user_id=current_user.id,
            agent_session_id=agent_id,
            image_bytes=image_bytes,
            observation_ref=observation_ref
        )
        
        # Update session status
        await agent_repo.update_status(
            user_id=current_user.id,
            agent_session_id=agent_id,
            status=new_state.status,
            termination_reason=new_state.termination_reason
        )
        
        return new_state
    except ValueError as e:
        import traceback
        with open("error_dump.txt", "w") as f:
            f.write(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        import traceback
        with open("error_dump.txt", "w") as f:
            f.write(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Agent step failed: {str(e)}")
