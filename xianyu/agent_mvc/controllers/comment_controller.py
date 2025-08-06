#coding=utf-8

import tornado.web
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session, sessionmaker
from models.comment import Comment
from models.user import User
from models.product import Product
from base.base import engine
from sqlalchemy import desc

Session = sessionmaker(bind=engine)


class CommentHandler(tornado.web.RequestHandler):
    """评价管理处理器"""
    
    def initialize(self):
        self.session = Session()

    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id")
        if user_id:
            return self.session.query(User).filter_by(id=int(user_id)).first()
        return None

    def get(self, product_id=None):
        """获取商品评价列表"""
        try:
            if product_id:
                # 获取特定商品的评价
                comments = self.session.query(Comment).filter_by(product_id=product_id).order_by(desc(Comment.created_at)).all()
                
                comments_data = []
                for comment in comments:
                    user = self.session.query(User).filter_by(id=comment.user_id).first()
                    comments_data.append({
                        'id': comment.id,
                        'content': comment.content,
                        'rating': comment.rating,
                        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'user_name': user.username if user else '匿名用户'
                    })
                
                self.write(json.dumps({'success': True, 'comments': comments_data}))
            else:
                # 获取所有评价
                comments = self.session.query(Comment).order_by(desc(Comment.created_at)).all()
                comments_data = []
                for comment in comments:
                    user = self.session.query(User).filter_by(id=comment.user_id).first()
                    product = self.session.query(Product).filter_by(id=comment.product_id).first()
                    comments_data.append({
                        'id': comment.id,
                        'content': comment.content,
                        'rating': comment.rating,
                        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'user_name': user.username if user else '匿名用户',
                        'product_name': product.name if product else '商品已删除'
                    })
                
                self.render('comments_list.html', comments=comments_data)
                
        except Exception as e:
            self.write(json.dumps({'success': False, 'error': str(e)}))

    def post(self):
        """发布评价"""
        try:
            user = self.get_current_user()
            if not user:
                self.write(json.dumps({'success': False, 'error': '请先登录'}))
                return

            product_id = int(self.get_argument("product_id"))
            content = self.get_argument("content")
            rating = float(self.get_argument("rating", 5.0))

            # 验证商品是否存在
            product = self.session.query(Product).filter_by(id=product_id).first()
            if not product:
                self.write(json.dumps({'success': False, 'error': '商品不存在'}))
                return

            # 检查用户是否已经评价过这个商品
            existing_comment = self.session.query(Comment).filter_by(
                user_id=user.id, 
                product_id=product_id
            ).first()
            
            if existing_comment:
                self.write(json.dumps({'success': False, 'error': '您已经评价过这个商品了'}))
                return

            # 创建新评价
            new_comment = Comment(
                user_id=user.id,
                product_id=product_id,
                content=content,
                rating=rating
            )
            
            self.session.add(new_comment)
            self.session.commit()
            
            self.write(json.dumps({
                'success': True, 
                'message': '评价发布成功',
                'comment_id': new_comment.id
            }))
            
        except Exception as e:
            self.session.rollback()
            self.write(json.dumps({'success': False, 'error': str(e)}))

    def delete(self, comment_id):
        """删除评价（仅限评价作者或管理员）"""
        try:
            user = self.get_current_user()
            if not user:
                self.write(json.dumps({'success': False, 'error': '请先登录'}))
                return

            comment = self.session.query(Comment).filter_by(id=comment_id).first()
            if not comment:
                self.write(json.dumps({'success': False, 'error': '评价不存在'}))
                return

            # 只有评价作者可以删除自己的评价
            if comment.user_id != user.id:
                self.write(json.dumps({'success': False, 'error': '只能删除自己的评价'}))
                return

            self.session.delete(comment)
            self.session.commit()
            
            self.write(json.dumps({'success': True, 'message': '评价删除成功'}))
            
        except Exception as e:
            self.session.rollback()
            self.write(json.dumps({'success': False, 'error': str(e)}))

    def on_finish(self):
        self.session.close()


class ProductRatingHandler(tornado.web.RequestHandler):
    """商品评分统计处理器"""
    
    def initialize(self):
        self.session = Session()

    def get(self, product_id):
        """获取商品评分统计"""
        try:
            # 计算平均评分和评价数量
            from sqlalchemy import func
            result = self.session.query(
                func.avg(Comment.rating).label('avg_rating'),
                func.count(Comment.id).label('comment_count')
            ).filter_by(product_id=product_id).first()
            
            avg_rating = round(float(result.avg_rating), 1) if result.avg_rating else 0
            comment_count = result.comment_count or 0
            
            # 获取评分分布
            rating_distribution = {}
            for i in range(1, 6):
                count = self.session.query(Comment).filter_by(
                    product_id=product_id
                ).filter(Comment.rating == i).count()
                rating_distribution[i] = count
            
            self.write(json.dumps({
                'success': True,
                'avg_rating': avg_rating,
                'comment_count': comment_count,
                'rating_distribution': rating_distribution
            }))
            
        except Exception as e:
            self.write(json.dumps({'success': False, 'error': str(e)}))

    def on_finish(self):
        self.session.close()
