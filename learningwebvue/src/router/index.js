import {createRouter, createWebHashHistory, createWebHistory} from 'vue-router'
import NoteList from '../views/NoteList.vue'
import NoteDetail from '../views/NoteDetail.vue'
import TestChat from "@/views/TestChat.vue";
import TestKnowledgePoint from "@/views/TestKnowledgePoint.vue";
import TestQuestionComponent from "@/views/TestQuestionComponent.vue";
import Login from "@/views/Login.vue";

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Login,
  },{
    path: '/NoteList',
    name: 'NoteList',
    component: NoteList
  },
  {
    path: '/note/:noteId',
    component: () => import('@/views/NoteDetail.vue')
  },
  {
    path:'/aiChat',
    name:"aiChat",
    component: TestChat
  },
  {
    path:'/testKnowledge',
    name:"testKnowledge",
    component: TestKnowledgePoint
  },
  {
    path:'/testQuestionComponent',
    name:"testQuestionComponent",
    component: TestQuestionComponent
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router