# 대화창 스타일 댓글 시스템 설계

## 💡 핵심 아이디어

기존의 계층형 댓글(댓글→대댓글→대대댓글) 구조 대신, **각 댓글이 독립된 대화방을 만들어 카카오톡처럼 핑퐁 대화**를 할 수 있는 시스템

## 🎯 기본 개념

```
📝 원글

💬 사용자A의 대화방
├── 사용자A: "첫 번째 댓글"
├── 원글작성자: "답변입니다"
├── 사용자A: "고맙습니다"
└── 원글작성자: "천만에요"

💬 사용자B의 대화방
├── 사용자B: "두 번째 댓글"
└── 원글작성자: "네 맞아요"

💬 사용자C의 대화방
└── 사용자C: "세 번째 댓글" (아직 대화 없음)
```

## 🔧 DB 모델 설계

```python
class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    thread_id = Column(Integer)  # 🔑 대화방 ID (첫 댓글의 ID)
    
    content = Column(Text, nullable=False)
    author = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    is_thread_starter = Column(Boolean, default=False)  # 대화 시작 댓글인지
```

### 핵심 로직

1. **새 댓글 작성**: `thread_id = comment.id` (자신이 대화방 주인)
2. **대화 참여**: 기존 `thread_id` 사용
3. **대화방 구분**: `thread_id`로 그룹핑

## 🚀 구현 로직

### 댓글 생성

```python
def create_comment(post_id: int, content: str, author: str, reply_to_thread: int = None):
    if reply_to_thread:
        # 기존 대화에 참여
        comment = Comment(
            post_id=post_id,
            thread_id=reply_to_thread,
            content=content,
            author=author,
            is_thread_starter=False
        )
    else:
        # 새 대화 시작
        comment = Comment(
            post_id=post_id,
            thread_id=None,  # 나중에 자신의 ID로 업데이트
            content=content,
            author=author,
            is_thread_starter=True
        )
        db.add(comment)
        db.flush()
        comment.thread_id = comment.id  # 🔑 자신의 ID를 thread_id로 설정
    
    return comment
```

### 대화방 조회

```python
def get_conversations(post_id: int):
    comments = db.query(Comment)\
        .filter(Comment.post_id == post_id)\
        .order_by(Comment.thread_id, Comment.created_at)\
        .all()
    
    # thread_id별로 그룹핑
    conversations = {}
    for comment in comments:
        thread_id = comment.thread_id
        if thread_id not in conversations:
            conversations[thread_id] = []
        conversations[thread_id].append(comment)
    
    return conversations
```

## 🎨 카카오톡 스타일 연속 메시지 그룹핑

### 핵심 아이디어
- 같은 사람이 연속으로 메시지를 보내면 **첫 메시지에만 프로필 표시**
- 시간차가 5분 이상 나거나 다른 사람이 메시지를 보내면 **새 그룹으로 분리**

### 실시간 계산 방식 (추천)

```javascript
function shouldShowProfile(currentComment, prevComment) {
  if (!prevComment) return true;  // 첫 메시지
  
  if (currentComment.author !== prevComment.author) return true;  // 작성자 다름
  
  const timeDiff = new Date(currentComment.created_at) - new Date(prevComment.created_at);
  if (timeDiff > 5 * 60 * 1000) return true;  // 5분 이상 차이
  
  return false;  // 연속 메시지
}
```

### 프런트엔드 렌더링

```jsx
function ConversationThread({ comments }) {
  const processedComments = comments.map((comment, index) => {
    const prevComment = comments[index - 1];
    const showProfile = shouldShowProfile(comment, prevComment);
    return { ...comment, showProfile };
  });

  return (
    <div className="conversation-thread">
      {processedComments.map((comment) => (
        <div key={comment.id} className="message">
          {comment.showProfile && (
            <div className="profile">
              <img src={`/profiles/${comment.author}.jpg`} />
              <span>{comment.author}</span>
            </div>
          )}
          <div className="message-content">
            {comment.content}
          </div>
        </div>
      ))}
    </div>
  );
}
```

## 💡 핵심 장점

1. **직관적**: 각 댓글이 독립된 대화방
2. **깔끔한 UI**: 카카오톡처럼 친숙한 인터페이스
3. **단순한 로직**: thread_id만으로 그룹핑
4. **확장 가능**: 대화별 알림, 숨기기 등 기능 추가 용이

## 🛠 구현 시 고려사항

### DB 인덱스
```sql
CREATE INDEX idx_comments_thread ON comments(post_id, thread_id, created_at);
```

### API 엔드포인트
```python
# 대화방 목록 조회
GET /posts/{post_id}/conversations

# 특정 대화방 조회  
GET /posts/{post_id}/conversations/{thread_id}

# 새 댓글 (새 대화방)
POST /posts/{post_id}/comments

# 대화 참여
POST /posts/{post_id}/conversations/{thread_id}/comments
```

### 프런트엔드 상태 관리
- 대화방별로 컴포넌트 분리
- 실시간 업데이트 (WebSocket 고려)
- 무한 스크롤 (오래된 메시지 페이징)

## 🎯 결과물

전통적인 계층형 댓글 대신 **메신저 앱 같은 친근하고 직관적인 댓글 시스템**을 구현할 수 있음