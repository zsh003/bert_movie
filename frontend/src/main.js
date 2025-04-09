import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import {
  Layout,
  Menu,
  Row,
  Col,
  Card,
  List,
  Avatar,
  Tag,
  Divider,
  PageHeader,
  Select,
  Pagination,
  Comment
} from 'ant-design-vue'
import {antd} from 'ant-design-vue'
import 'ant-design-vue/dist/antd.css'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// app.use(Layout)
// app.use(Menu)
// app.use(Row)
// app.use(Col)
// app.use(Card)
// app.use(List)
// app.use(Avatar)
// app.use(Tag)
// app.use(Divider)
// app.use(PageHeader)
// app.use(Select)
// app.use(Pagination)
// app.use(Comment)
app.use(antd)

app.use(createPinia())
app.use(router)

app.mount('#app') 