<template>
  <el-form :rules="rules" :model="ruleForm" ref="ruleForm" >
    <el-form-item label="用户名">
      <el-input v-model.trim="user.name" :disabled="true" />
    </el-form-item>
    <el-form-item label="邮箱">
      <el-input v-model.trim="user.email" :disabled="true" />
    </el-form-item>
    <el-form-item label="Licence">
      <el-input v-model.trim="user.licence" class="copy-code-button" :disabled="true">
        <el-button slot="append" icon="el-icon-document-copy" class="copy-code-button" :data-clipboard-text="user.licence" @click="copy">
        </el-button>
      </el-input>
    </el-form-item>
    <el-form-item label="旧密码" v-if="updatePwd === true">
      <el-input v-model.trim="ruleForm.oldPassword" />
    </el-form-item>
    <el-form-item label="新密码" v-if="updatePwd === true" prop="pass">
      <el-input type="password" v-model.trim="ruleForm.pass" />
    </el-form-item>
    <el-form-item label="确认新密码" v-if="updatePwd === true" prop="checkPass">
      <el-input type="password" v-model.trim="ruleForm.checkPass" />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="handleUpdatePwd" v-if="updatePwd === true">修改</el-button>
      <el-button type="primary" @click="handlerPwd" v-if="updatePwd === false">修改密码</el-button>
      <el-button type="primary" @click="closeHandlerPwd" v-if="updatePwd === true">关闭</el-button>
    </el-form-item>
  </el-form>
</template>

<script>
import { updatePassword } from "@/api/user"
import Clipboard from 'clipboard'

export default {
  data(){
    const validatePass = (rule, value, callback) => {
        if (value === '') {
          callback(new Error('请输入密码'));
        } else {
          if (this.ruleForm.pass.length<8){
            callback(new Error('密码不能少于8位'));
          }
          if (this.ruleForm.checkPass !== '') {
            this.$refs.ruleForm.validateField('checkPass');
          }
          callback();
        }
      };
    const validatePass2 = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'));
      } else if (value !== this.ruleForm.pass) {
        callback(new Error('两次输入密码不一致!'));
      } else {
        callback();
      }
    };
    return{
      ruleForm:{
        name: '',
        email: '',
        oldPassword:"",
        pass:"",
        checkPass:""
      },
      updatePwd:false,
      rules: {
        pass: [
          { validator: validatePass, trigger: 'blur' }
        ],
        checkPass: [
          { validator: validatePass2, trigger: 'blur' }
        ],
      },
    }
  },
  props: {
    user: {
      type: Object,
      default: () => {
        return {
          name: '',
          email: '',
        }
      }
    }
  },
  methods: {
    handlerPwd(){
      this.updatePwd = true
    },
    closeHandlerPwd(){
      this.updatePwd = false
    },
    copy () {
      let clipboard = new Clipboard('.copy-code-button') // 这里可以理解为选择器，选择上面的复制按钮
        clipboard.on('success', e => {
            clipboard.destroy()
            this.$message({
              message: '复制成功',
              type: "success",
            })
        })
        clipboard.on('error', e => {
          clipboard.destroy()
          this.$message({
            message: '复制失败',
            type: "error",
        })
      })
    },
    handleUpdatePwd(){
      this.$refs.ruleForm.validate(valid => {
        if(valid){
          updatePassword(this.ruleForm).then(response=>{
            let data = response.data
            if (data.code === 200){
              this.$message({
              message: '修改密码成功',
              type: "success",
              })
              this.updatePwd = false
            }else{
              this.$message({
              message: data.msg,
              type: "error",
              })
            }
          })
        }else {
          return false
        }
      })
    },
  }
}
</script>
