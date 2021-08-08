<template>
  <div class="container">
    <div class="widget">
      <el-tabs type="border-card" v-loading='loading' element-loading-text="正在安装相关镜像"
               element-loading-spinner="el-icon-loading"
               element-loading-background="rgba(0, 0, 0, 0.1)" >
        <el-tab-pane id="ceshi">
          <span slot="label"><i class="el-icon-document"></i>DockerCompose</span>
          <el-form :model=composeForm inline ref="build" size="mini" :rules="rules">
            <el-form-item label="名称" prop="tag1">
              <el-input v-model="composeForm.tag1" placeholder="eg. redis:latest"></el-input>
            </el-form-item>
          </el-form>
          <el-tabs value="dockerfile" ref="tab">
            <el-tab-pane name="dockerfile">
              <span slot="label"><i class="el-icon-edit"></i> DockerCompose.yml</span>
              <div>
                <el-form>
                  <el-form-item>
                    <el-input v-model="compose_content" type="textarea" rows="10"
                              placeholder="Define or paste the content of Your DockerCompose.yml here"></el-input>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>
          </el-tabs>
          <div>
            <div class="wd-title">Actions</div>
            <div class="action-group">
              <el-button @click="compose_build" type="primary" size="mini">编译</el-button>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script>
import { build_compose,show_build_status } from "@/api/layout"
import { getTask,batchTask,progressTask } from '@/api/tasks'

export default {
  inject: ['reload'],
  data() {
    return {
      rules: {
        tag: [
          {required: true, max: 100, min: 2, message: "请输入要构建的镜像名称"}
        ],
        tag1:[
          {required: true, max: 100, min: 2, message: "请输入要构建的docker-compose名称"}
        ]
      },
      selectHub: 'DockerHub',
      imageName: '',
      buildForm: {
        tag: '',
      },
      composeForm:{
        tag1:'',
      },
      options: [{
        value: 'DockerHub',
        label: 'DockerHub'
      }],
      file: null,
      output: [],
      pk: null,
      content: '',
      compose_content:"",
      listTotal: 0,
      listData: [],
      showLog: false,
      loading: false,
    }
  },
  created() {
    this.showCompose()
  },
  methods:{
    showCompose(){
      show_build_status().then(response=>{
        console.log(response.data)
        if (response.data.code === 200){
          let data = response.data['data']
          let img_name = response.data['img_name']
          this.compose_content = data
          this.composeForm.tag1 = img_name
          this.loading = true
        }else {
        }
      })
    },
    compose_build(){
      let data = {}
      data.compose_content = this.compose_content
      data.tag = this.composeForm.tag1

      build_compose(data).then(response=>{
        if (response.data.code === 200){
          this.$message({
            title: '构建任务创建成功',
            message: response.data.message,
            type: 'success'
          });
          this.reload()
        }else {
          this.$message({
            title: '构建任务创建失败',
            message: response.data.message,
            type: 'error'
          });

        }
      })
    }
  }
}
</script>

<style scoped>
.small {
  font-size: 80%;
}
.btn-group svg {
  width: 14px;
  height: 14px;
  margin-right: 4px;
}
.wd-title {
  padding: 10px 6px;
  color: #777;
  border-bottom: 1px solid #777;
}
.action-group {
  padding: 10px 6px;
}
.pre {
  padding: 0 15px;
  color: #000;
  font-size: 13px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.line {
  margin-block-start: 2px;
  margin-block-end: 2px;
}
</style>
