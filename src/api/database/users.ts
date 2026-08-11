import { DatabaseErrorCode } from '@/constant';
import {
  ClientUser,
  getLoginUser as databaseGetLoginUser,
  insertLoginUser as databaseInsertLoginUser,
  updateLoginUser as databaseUpdateLoginUser,
} from '@/sqls';
import {
  formatResponse,
  converSqlExecResult,
  convertToSnakeCaseObject,
  convertObjectField,
  deserializeArrayFields,
  serializeArrayFields,
} from '@/utils';
import { getInstance } from './instance';

const USER_ARRAY_FIELDS = ['permissions'];

export async function getLoginUser(userID: string): Promise<string> {
  try {
    const db = await getInstance();

    const execResult = databaseGetLoginUser(db, userID);

    if (execResult.length === 0) {
      return formatResponse(
        '',
        DatabaseErrorCode.ErrorNoRecord,
        `no login user with id ${userID}`
      );
    }

    const result = converSqlExecResult(execResult[0], 'CamelCase', [], {
      name: 'nickname',
    })[0];

    return formatResponse(
      result && deserializeArrayFields(result, USER_ARRAY_FIELDS)
    );
  } catch (e) {
    console.error(e);

    return formatResponse(
      undefined,
      DatabaseErrorCode.ErrorInit,
      JSON.stringify(e)
    );
  }
}

export async function insertLoginUser(userStr: string): Promise<string> {
  try {
    const db = await getInstance();
    const user = convertToSnakeCaseObject(
      serializeArrayFields(
        convertObjectField(JSON.parse(userStr), { nickname: 'name' }),
        USER_ARRAY_FIELDS
      )
    ) as ClientUser;

    const execResult = databaseInsertLoginUser(db, user);

    return formatResponse(execResult);
  } catch (e) {
    console.error(e);

    return formatResponse(
      undefined,
      DatabaseErrorCode.ErrorInit,
      JSON.stringify(e)
    );
  }
}

export async function updateLoginUser(userStr: string): Promise<string> {
  try {
    const db = await getInstance();
    const user = convertToSnakeCaseObject(
      serializeArrayFields(
        convertObjectField(JSON.parse(userStr), { nickname: 'name' }),
        USER_ARRAY_FIELDS
      )
    ) as ClientUser;

    const execResult = databaseUpdateLoginUser(db, user);
    const modifed = db.getRowsModified();
    if (modifed === 0) {
      throw 'updateLoginUser no record updated';
    }
    return formatResponse(execResult);
  } catch (e) {
    console.error(e);

    return formatResponse(
      undefined,
      DatabaseErrorCode.ErrorInit,
      JSON.stringify(e)
    );
  }
}
