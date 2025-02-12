// IMPORTANT: This is compiled to js so the __dirname is the *JS FOLDER*
const path = require('path')
export const rootDir:string = path.resolve(__dirname+"/../")+"/";
export const frontendDir:string = path.resolve(__dirname+'/../static/')+"/";
export const jsDir:string = path.resolve(__dirname+'/static/')+"/"
export const port = 3000
// account expiries for:    user accounts, admins,   super-admins
export const expiry = [0, 1000*60*60*24, 1000*60*30, 1000*60*5];
